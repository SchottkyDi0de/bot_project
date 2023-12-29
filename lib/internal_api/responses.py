from lib.data_classes.internal_api.inf_response import InfoResponse
from lib.data_classes.internal_api.err_response import ErrorResponse

class InfoResponses:
    player_updated = InfoResponse.model_validate(
        {   
            'info' : 'Success',
            'message': 'Player data has ben updated',
            'code': 200
        }
    )
    pong = InfoResponse.model_validate(
        {   
            'info' : 'Success',
            'message': 'Pong',
            'code': 200
        }
    )

class ErrorResponses():
    base_model = ErrorResponse.model_validate(
        {
            'error': 'Error', 
            'message': 'Error [INTERNAL ERROR]',
            'code': 505
        }
    )
    method_not_allowed =  ErrorResponse.model_validate(
        {
            'error': 'MethodNotAllowed', 
            'message': 'Root method of API not allowed',
            'code': 500
        }
    )
    acces_denied =  ErrorResponse.model_validate(
        {
            'error': 'AccesDenied', 
            'message': 'Invalid API key, acces denied',
            'code': 501
        }
    )
    player_not_found = ErrorResponse.model_validate(
        {
            'error': 'PlayerNotFound', 
            'message': 'Player not found in DB',
            'code': 502
        }
    )
    player_session_not_found = ErrorResponse.model_validate(
        {
            'error': 'PlayerSessionNotFound', 
            'message': 'Player session not found in DB',
            'code': 504
        }
    )
    validation_error = ErrorResponse.model_validate(
        {
            'error': 'ValidationError', 
            'message': 'Error while validating data [INTERNAL ERROR]',
            'code': 503
        }
    )
    set_not_allowed = ErrorResponse.model_validate(
        {
            'error': 'SetNotAlowed', 
            'message': 'Set player not allowed, some fields is read only',
            'code': 506
        }
    )