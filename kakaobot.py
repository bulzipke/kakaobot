from enum import Enum
from flask import Flask, jsonify

TYPE = 'type'
TEXT = 'text'
BUTTONS = 'buttons'


class KeyboardType(Enum):
    text = TEXT
    buttons = BUTTONS


class KakaoBot:
    app = Flask(__name__)

    def __init__(self):
        self._keyboard_type = KeyboardType.text
        self._button_list = list()

    def set_keyboard(self, value):
        if not isinstance(value, KeyboardType):
            raise Exception('{} {}'.format(value, 'is not a valid keyboard type.'))
        self._keyboard_type = value

    def set_button_list(self, value):
        if not isinstance(value, list):
            raise Exception('{} {}'.format(value, 'is not a list.'))
        self._button_list = value

    def start(self, port=7000):
        try:
            self.app.run(threaded=True, debug=False, port=port)
        except OSError as e:
            raise e

    @app.route('/keyboard/', methods=['GET'])
    def keyboard(self):
        res = {TYPE: self._keyboard_type}
        if self._keyboard_type is KeyboardType.buttons:
            res[BUTTONS] = self._button_list
        return jsonify(res)




