request_not_permitted = {
    'status': 'failed',
    'description': 'html request type not permitted'
}

success_200 = {'Status': 'success', 'Code': '200 OK', 'Description': 'process terminated successfully', 'Connection': 'close'}

success_201 = {'Status': 'success', 'Code': '201 Created', 'Description': 'content created in database', 'Connection': 'close'}

error_400 = {'Status': 'failure', 'Code': '400 Bad Request', 'Description': 'request was improperly formatted', 'Connection': 'close'}

error_404 = {'Status': 'failure', 'Code': '404 Not Found', 'Description': 'page not found', 'Connection': 'close'}

error_405 = {'Status': 'failure', 'Code': '405 Method Not Allowed', 'Description': 'html request type not permitted', 'Connection': 'close'}
