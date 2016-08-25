from .lightstreamer import LSClient


class NadexStreamApi(object):

    def __init__(self, account, rest_api):
        self._base_url = compat.parse_url(account.lightstreamerEndpoint)
        self._adapter_set = "InVisionProvider"
        self._user = account.currentAccountId
        self._password = 'XST-{}'.format(rest_api.connection.get_xst())
        self._session = {}
        self._subscriptions = {}
        self._current_subscription_key = 0
        self._stream_connection = None
        self._stream_connection_thread = None

    def _encode_params(self, params):
        """Encode the parameter for HTTP POST submissions, but
        only for non empty values..."""
        return compat._url_encode(
                dict([(k, v) for (k, v) in compat._iteritems(params) if v])
        )

    def _call(self, base_url, url, body):
        """Open a network connection and performs HTTP Post
        with provided body.
        """
        # Combines the "base_url" with the
        # required "url" to be used for the specific request.
        url = compat.urljoin(base_url.geturl(), url)
        # logger.debug("urlopen %s with data=%s" % (url, body))
        return compat._urlopen(url, data=self._encode_params(body))  # str_to_bytes

    def _set_control_link_url(self, custom_address=None):
        """Set the address to use for the Control Connection
        in such cases where Lightstreamer is behind a Load Balancer.
        """
        if custom_address is None:
            self._control_url = self._base_url
        else:
            parsed_custom_address = compat.parse_url("//" + custom_address)
            self._control_url = parsed_custom_address._replace(
                    scheme=self._base_url[0]
            )

    def _control(self, params):
        """Create a Control Connection to send control commands
        that manage the content of Stream Connection.
        """
        params["LS_session"] = self._session["SessionId"]
        response = self._call(self._control_url, CONTROL_URL_PATH, params)
        return response.readline().decode("utf-8").rstrip()

    def _get_stream(self):
        """Read a single line of content of the Stream Connection."""
        line = self._stream_connection.readline().decode("utf-8").rstrip()
        return line

    def connect(self):
        """Establish a connection to Lightstreamer Server to create
        a new session.
        """
        self._stream_connection = self._call(
                self._base_url,
                CONNECTION_URL_PATH,
                {
                    # "LS_op2": 'create',
                    # "LS_cid": 'mgQkwtwdysogQz2BJ4Ji kOj2Bg',
                    "LS_adapter_set": self._adapter_set,
                    "LS_user": self._user,
                    "LS_password": self._password}
        )
        server_response = self._get_stream()
        if server_response == OK_CMD:
            # Parsing session information
            while 1:
                line = self._get_stream()
                if line:
                    session_key, session_value = line.split(":", 1)
                    self._session[session_key] = session_value
                else:
                    break

            # Setup of the control link url
            self._set_control_link_url(self._session.get("ControlAddress"))

            # Start a new thread to handle real time updates sent
            # by Lightstreamer Server on the stream connection.
            self._stream_connection_thread = threading.Thread(
                    name="STREAM-CONN-THREAD",
                    target=self._receive
            )
            self._stream_connection_thread.setDaemon(True)
            self._stream_connection_thread.start()
        else:
            lines = self._stream_connection.readlines()
            lines.insert(0, server_response)
            logger.error("Server response error: \n%s" % "".join(lines))
            raise IOError()

    def _join(self):
        """Await the natural STREAM-CONN-THREAD termination."""
        if self._stream_connection_thread:
            logger.debug("Waiting for STREAM-CONN-THREAD to terminate")
            self._stream_connection_thread.join()
            self._stream_connection_thread = None
            logger.debug("STREAM-CONN-THREAD terminated")

    def disconnect(self):
        """Request to close the session previously opened with
        the connect() invocation.
        """
        if self._stream_connection is not None:
            # Close the HTTP connection
            self._stream_connection.close()
            logger.debug("Connection closed")
            # self._join()
            print("DISCONNECTED FROM LIGHTSTREAMER")
        else:
            logger.warning("No connection to Lightstreamer")

    def destroy(self):
        """Destroy the session previously opened with
        the connect() invocation.
        """
        if self._stream_connection is not None:
            server_response = self._control({"LS_op": OP_DESTROY})
            if server_response == OK_CMD:
                # There is no need to explicitly close the connection,
                # since it is handled by thread completion.
                self._join()
            else:
                logger.warning("No connection to Lightstreamer")

    def subscribe(self, subscription):
        """"Perform a subscription request to Lightstreamer Server."""
        # Register the Subscription with a new subscription key
        self._current_subscription_key += 1
        self._subscriptions[self._current_subscription_key] = subscription

        # Send the control request to perform the subscription
        self._control({
            "LS_table": self._current_subscription_key,
            "LS_op": OP_ADD,
            #"LS_data_adapter": subscription.adapter,
            "LS_mode": subscription.mode,
            "LS_schema": " ".join(subscription.field_names),
            "LS_id": " ".join(subscription.item_names),
            "LS_requested_max_frequency": 1,  # rate limiting per second. "unlimited" for no limit
            "LS_snapshot": "true",  # fetch from the last snapshot
        })
        return self._current_subscription_key

    def unsubscribe(self, subscription_key):
        """Unregister the Subscription associated to the
        specified subscription_key.
        """
        if subscription_key in self._subscriptions:
            server_response = self._control({
                "LS_Table": subscription_key,
                "LS_op": OP_DELETE
            })
            logger.debug("Server response ---> <%s>", server_response)

            if server_response == OK_CMD:
                del self._subscriptions[subscription_key]
                logger.info("Unsubscribed successfully")
            else:
                logger.warning("Server error")
        else:
            logger.warning("No subscription key %d found!" % subscription_key)

    def _forward_update_message(self, update_message):
        """Forwards the real time update to the relative
        Subscription instance for further dispatching to its listeners.
        """
        logger.debug("Received update message ---> <%s>", update_message)
        idx = update_message.index(',')
        tok = update_message[:idx]
        table, item = int(tok), update_message[idx+1:]
        if table in self._subscriptions:
            self._subscriptions[table].notifyupdate(item)
        else:
            logger.warning("No subscription found!")

    def _receive(self):
        receive = True
        while receive:
            logger.debug("Waiting for a new message")
            try:
                message = self._get_stream()
                logger.debug("Received message ---> <%s>" % message)
            except Exception:
                logger.error("Communication error")
                print(traceback.format_exc())
                message = None

            if message is None:
                receive = False
                logger.warning("No new message received")
            elif message == PROBE_CMD:
                # Skipping the PROBE message, keep on receiving messages.
                logger.debug("PROBE message")
            elif message.startswith(ERROR_CMD):
                # Terminate the receiving loop on ERROR message
                receive = False
                logger.error("ERROR")
            elif message.startswith(LOOP_CMD):
                # Terminate the the receiving loop on LOOP message.
                # A complete implementation should proceed with
                # a rebind of the session.
                logger.debug("LOOP")
                receive = False
            elif message.startswith(SYNC_ERROR_CMD):
                # Terminate the receiving loop on SYNC ERROR message.
                # A complete implementation should create a new session
                # and re-subscribe to all the old items and relative fields.
                logger.error("SYNC ERROR")
                receive = False
            elif message.startswith(END_CMD):
                # Terminate the receiving loop on END message.
                # The session has been forcibly closed on the server side.
                # A complete implementation should handle the
                # "cause_code" if present.
                logger.info("Connection closed by the server")
                receive = False
            elif message.startswith("Preamble"):
                # Skipping Preamble message, keep on receiving messages.
                logger.debug("Preamble")
            else:
                self._forward_update_message(message)

        logger.debug("Closing connection")
        # Clear internal data structures for session
        # and subscriptions management.
        # self._stream_connection.close()
        self._stream_connection = None
        self._session.clear()
        self._subscriptions.clear()
        self._current_subscription_key = 0
