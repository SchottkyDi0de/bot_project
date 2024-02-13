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
    data_was_sent = InfoResponse.model_validate(
        {
            'info' : 'Data sent successfully',
            'message' : '...',
            'code': 200
        }
    )
    image_settings_updated = InfoResponse.model_validate(
        {
            'info' : 'Success',
            'message': 'Image settings has ben updated',
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
    internal_error = ErrorResponse.model_validate(
        {
            'error': 'Error', 
            'message': 'Error [INTERNAL ERROR]',
            'code': 500
        }
    )
    method_not_allowed =  ErrorResponse.model_validate(
        {
            'error': 'MethodNotAllowed', 
            'message': 'Root method of API not allowed',
            'code': 405
        }
    )
    acces_denied =  ErrorResponse.model_validate(
        {
            'error': 'A`m a teapot', 
            'message': 'Invalid API key, acces denied',
            'code': 418
        }
    )
    player_not_found = ErrorResponse.model_validate(
        {
            'error': 'PlayerNotFound', 
            'message': 'Player not found in DB',
            'code': 400
        }
    )
    player_session_not_found = ErrorResponse.model_validate(
        {
            'error': 'PlayerSessionNotFound', 
            'message': 'Session expired / not started',
            'code': 400
        }
    )
    validation_error = ErrorResponse.model_validate(
        {
            'error': 'ValidationError', 
            'message': 'Error while validating data. Check the data struct and try again',
            'code': 400
        }
    )
    set_not_allowed = ErrorResponse.model_validate(
        {
            'error': 'SetNotAlowed', 
            'message': 'Set player not allowed, some fields is read only',
            'code': 405
        }
    )