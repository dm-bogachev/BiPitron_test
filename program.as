.INTER_PANEL_D
0,14,"tcp.ip","IP:","",10,9,0
1,8,"tcp.port","Port:","",10,9,5,1,0
6,10,"Execute ","autostart","","",10,4,9,1,"PCEXEC autostart.pc",0
13,10,"Abort","autostart","","",10,4,9,2,"PCABORT",0
21,8,"tyterm","Terminal","",10,15,2,1,0
.END
.INTER_PANEL_TITLE
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
"",0
.END
.INTER_PANEL_COLOR_D
182,3,224,244,28,159,252,255,251,255,0,31,2,241,52,219,
.END
.PROGRAM tcp.client.pc ()
  DO
    ; Checking for active sockets and closing them
    PRINT tyterm: "Checking for active sockets and closing them"
    TCP_STATUS .number, .ports[0], .sockets[0], .errors[0], .suberrors[0], .$ips[0]
    IF .number > 0 THEN
      FOR .i = 0 TO .number - 1
        IF .sockets[.i] <> 0 THEN
          PRINT tyterm: "Closing socket with id: ", .sockets[.i]
          TCP_CLOSE .status, .sockets[.i]
        END
      END
    END
    ;
    ; Get IP from string
    $tcp.ip.copy = $tcp.ip
    FOR .i = 1 TO 4
      .$ip = $DECODE ($tcp.ip.copy, ".", 0)
      ip[.i] = VAL (.$ip)
      IF .i < 4 THEN
        .$ip = $DECODE ($tcp.ip.copy, ".", 1)
      END
    END
    ;
    ; Connect to server
    PRINT tyterm: "Connecting to server with ip: " + $tcp.ip
    TCP_CONNECT tcp.socket, tcp.port, ip[1], tcp.connect.tmo
    ;
    ; Start data processing cycle
    IF tcp.socket >= 0 THEN
      PRINT tyterm: "Connection established with socket id:", tcp.socket
      .connected = TRUE
      ;
      ; Start receiving data cycle
      tcp.error.cnt = 0
      WHILE .connected AND tcp.error.cnt <= tcp.retry.count AND tcp.abort == FALSE DO
        TCP_RECV .status, tcp.socket, .$tcp.request[1], .request.size, tcp.receive.tmo, 255
        IF .status >= 0 THEN
          IF .request.size == 0 THEN
            tcp.error.cnt = tcp.error.cnt + 1
            PRINT tyterm: "Received data with 0 length. Error count:", tcp.error.cnt
          ELSE
            ;PRINT tyterm: .$tcp.request[1]
            CALL tcp.callback.pc (.$tcp.request[], .request.size)
          END
        ELSE
          ;tcp.error.cnt = tcp.error.cnt + 1
          PRINT tyterm: "Failed to receive data with error:", .status, ". Error count:", tcp.error.cnt
        END
      END
    ELSE
      PRINT tyterm: "Connection failed with error:", tcp.socket
      IF tcp.socket > 0 THEN
        TCP_CLOSE .status, tcp.socket
      END
    END
    ;
  UNTIL tcp.abort == TRUE
  IF tcp.socket > 0 THEN
    TCP_CLOSE .status, tcp.socket
  END
  ;
.END
.PROGRAM tcp.send.pc (.$data[],.data.length)
  ;
  IF tcp.socket > 0 THEN
    TCP_SEND .status, tcp.socket, .$data[1], .data.length, tcp.send.tmo
    IF .status >= 0 THEN
      PRINT tyterm: "Sent ", .data.length, " strings"
      FOR .i = 1 TO .data.length
        IF LEN (.$data[.i]) > 127 THEN
          PRINT tyterm: /S, .i, ": "
          PRINT tyterm: /S, $LEFT (.$data[.i], 128)
          PRINT tyterm: $MID (.$data[.i], 129)
        ELSE
          PRINT tyterm: /S, .i, ": "
          PRINT tyterm: .$data[.i]
        END
      END
    ELSE
      tcp.error.cnt = tcp.error.cnt + 1
      PRINT tyterm: "Failed to send data with error:", .status, ". Error count:", tcp.error.cnt
    END
  ELSE
    PRINT tyterm: "Failed to send data. Socket is not opened"
  END
  ;
.END
.PROGRAM tcp.callback.pc (.$data[],.data.length)
  PRINT tyterm: "Received ", .data.length, " strings"
  FOR .i = 1 TO .data.length
    IF LEN (.$data[.i]) > 127 THEN
      PRINT tyterm: /S, .i, ": "
      PRINT tyterm: /S, $LEFT (.$data[.i], 128)
      PRINT tyterm: $MID (.$data[.i], 129)
    ELSE
      PRINT tyterm: /S, .i, ": "
      PRINT tyterm: .$data[.i]
    END
  END
  ;
  $type = ""
  IF INSTR (.$data[1], ";") <> 0 THEN
    $type = $DECODE (.$data[1], ";", 0)
    .$temp = $DECODE (.$data[1], ";", 1)
  ELSE
    $type = .$data[1]
  END
  ;
  SCASE $type OF
    SVALUE "PICK":
      ;CALL parse.cmd.pc (.$data[], .data.length)
      PRINT tyterm: "PICK"
      RETURN
    SVALUE "MEASUREMENT":
      PRINT tyterm: "MEASUREMENT"
      ;CALL parse.motion.pc (.$data[], .data.length)
      RETURN

  END
  ;
  PRINT tyterm: "Unhandled message. Return ALIVE"
  .$data[1] = "ALIVE"
  CALL tcp.send.pc (.$data[], 1)
.END
.PROGRAM autostart.pc ()
  CALL initialize.pc
  CALL tcp.client.pc
.END
.PROGRAM initialize.pc ()
  IF NOT EXISTREAL ("tyterm") THEN
    tyterm = 1
  END
  IF NOT EXISTCHAR ("$tcp.ip") THEN
    $tcp.ip = "127"
  END
  IF NOT EXISTREAL ("tcp.port") THEN
    tcp.port = 48569
  END
  IF NOT EXISTREAL ("tcp.connect.tmo") THEN
    tcp.connect.tmo = 5
  END
  IF NOT EXISTREAL ("tcp.receive.tmo") THEN
    tcp.receive.tmo = 5
  END
  IF NOT EXISTREAL ("tcp.send.tmo") THEN
    tcp.send.tmo = 5
  END
  IF NOT EXISTREAL ("tcp.retry.count") THEN
    tcp.retry.count = 10
  END
  IF NOT EXISTREAL ("tcp.abort") THEN
    tcp.abort = FALSE
  END
  PRINT tyterm: "PC initialization complete"
.END
.PROGRAM errstart.pc ()
  IF ERROR == -34021 THEN
    MC ERESET
    TWAIT 0.5
    PCEXECUTE 1: tcp.client.pc
  END
  errstart.pc ON
.END
.PROGRAM Comment___ () ; Comments for IDE. Do not use.
	; @@@ PROJECT @@@
	; @@@ PROJECTNAME @@@
	; program
	; @@@ HISTORY @@@
	; @@@ INSPECTION @@@
	; @@@ CONNECTION @@@
	; Standard 1
	; 192.168.0.2
	; 23
	; @@@ PROGRAM @@@
	; Group:TCPIP:1
	; 1:tcp.client.pc:B
	; .number 
	; .ports 
	; .sockets 
	; .errors 
	; .suberrors 
	; .i 
	; .status 
	; .connected 
	; .request.size 
	; 1:tcp.send.pc:B
	; .$data[] 
	; .data.length 
	; .status 
	; .i 
	; 1:tcp.callback.pc:B
	; .$data[] 
	; .data.length 
	; .i 
	; 0:autostart.pc:B
	; 0:initialize.pc:B
	; 0:errstart.pc:B
	; @@@ TRANS @@@
	; @@@ JOINTS @@@
	; @@@ REALS @@@
	; @@@ STRINGS @@@
	; @@@ INTEGER @@@
	; @@@ SIGNALS @@@
	; @@@ TOOLS @@@
	; @@@ BASE @@@
	; @@@ FRAME @@@
	; @@@ BOOL @@@
	; tcp.abort 
	; @@@ DEFAULTS @@@
	; BASE: NULL
	; TOOL: NULL
	; @@@ WCD @@@
	; SIGNAME: sig1 sig2 sig3 sig4
	; SIGDIM: % % % %
.END
.REALS
tyterm = 0
tcp.port = 48569
tcp.connect.tmo = 5
tcp.receive.tmo = 5
tcp.send.tmo = 5
tcp.retry.count = 5
tcp.abort = 0
a.value = 0
ip[1] = 127
ip[2] = 0
ip[3] = 0
ip[4] = 1
o.value = 0
t.value = 1
tcp.error.cnt = 0
tcp.socket = 456
x.value = 0.5
y.value = 0
z.value = 0
motion.enable = 0
.END
.STRINGS
$tcp.ip = "127.0.0.1"
$cmd = "GET_STATE"
$tcp.ip.copy = ""
$type = "LOLIZE"
.END
