#!/usr/bin/env python3

# Test whether a first packet of non-CONNECT is rejected.

from mosq_test_helper import *

def do_test(proto_ver):
    rc = 1
    mid = 2
    publish_packet = mosq_test.gen_publish("pub/qos1/test", qos=1, mid=mid, payload="message", proto_ver=proto_ver)
    puback_packet = mosq_test.gen_puback(mid, proto_ver=proto_ver)

    port = mosq_test.get_port()
    broker = mosq_test.start_broker(filename=os.path.basename(__file__), port=port)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(("localhost", port))
        sock.send(publish_packet)
        data = sock.recv(1)
        sock.close()
        if len(data) == 0:
            rc = 0
    except socket.error as e:
        if e.errno == errno.ECONNRESET:
            # Connection has been closed by peer, this is the expected behaviour
            rc = 0
    except mosq_test.TestError:
        pass
    finally:
        broker.terminate()
        broker.wait()
        (stdo, stde) = broker.communicate()
        if rc:
            print(stde.decode('utf-8'))
            print("proto_ver=%d" % (proto_ver))
            exit(rc)


do_test(proto_ver=4)
do_test(proto_ver=5)
exit(0)
