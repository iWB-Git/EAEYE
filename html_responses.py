SUCCESS_200 = ({'Status': 'success', 'Code': '200 OK', 'Description': 'process terminated successfully', 'Connection': 'close'}, 200)

SUCCESS_201 = ({'Status': 'success', 'Code': '201 Created', 'Description': 'content created in database', 'Connection': 'close'}, 201)

ERROR_400 = ({'Status': 'failure', 'Code': '400 Bad Request', 'Description': 'request was improperly formatted', 'Connection': 'close'}, 400)

ERROR_404 = ({'Status': 'failure', 'Code': '404 Not Found', 'Description': 'page not found', 'Connection': 'close'}, 404)

ERROR_405 = ({'Status': 'failure', 'Code': '405 Method Not Allowed', 'Description': 'html request type not permitted', 'Connection': 'close'}, 405)
