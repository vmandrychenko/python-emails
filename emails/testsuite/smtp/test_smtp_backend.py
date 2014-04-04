# encoding: utf-8
from __future__ import unicode_literals
import os
import logging
import emails
from emails.smtp import SMTPBackend


TRAVIS_CI = os.environ.get('TRAVIS')
HAS_INTERNET_CONNECTION = not TRAVIS_CI


def test_send_to_unknow_host():
    server = SMTPBackend(host='invalid-server.invalid-domain-42.com', port=25)
    response = server.sendmail(to_addrs='s@lavr.me', from_addr='s@lavr.me',  msg='...')[0]
    assert response.status_code is None
    assert response.error is not None
    assert isinstance(response.error, IOError)
    print("response.error.errno=", response.error.errno)
    if HAS_INTERNET_CONNECTION:
        # IOError: [Errno 8] nodename nor servname provided, or not known
        assert response.error.errno==8


def test_smtp_reconnect(smtp_server):

    # Simulate server disconnection
    # Check that SMTPBackend will reconnect

    message_params = {'html':'<p>Test from python-emails',
                      'mail_from': 's@lavr.me',
                      'mail_to': 'sergei-nko@yandex.ru',
                      'subject': 'Test from python-emails'}

    server = SMTPBackend(host=smtp_server.host, port=smtp_server.port, debug=1)
    server.open()
    logging.debug('simulate socket disconnect')
    server.connection.sock.close()  # simulate disconnect
    response = server.sendmail(to_addrs='s@lavr.me',
                               from_addr='s@lavr.me',
                               msg=emails.html(**message_params) )
    print(response)


def test_smtp_dict(smtp_server):

    message_params = {'html':'<p>Test from python-emails',
                      'mail_from': 's@lavr.me',
                      'mail_to': 'sergei-nko@yandex.ru',
                      'subject': 'Test from python-emails'}

    response = emails.html(**message_params).send( smtp={'host':smtp_server.host, 'port':smtp_server.port} )

    print(response)



if __name__=="__main__":
    import sys
    import logging
    sys.path.insert(0, '..')
    logging.basicConfig(level=logging.DEBUG)
    test_send_to_unknow_host()

    from conftest import TestLamsonSmtpServer
    smtp_server = TestLamsonSmtpServer().get_server()
    test_smtp_reconnect(smtp_server)
