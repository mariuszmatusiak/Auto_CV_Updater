# Auto CV Updater - automatize your CV modifications
# Copyright (C) 2026 Mariusz Matusiak <coffeedrivenengineer@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#

import base64
from enum import StrEnum, Enum

class Encoder:

    class Method(Enum):
        BASE64 = 1

    class Coding(StrEnum):
        ASCII = "ascii"
        UTF8  = "utf-8"

    def encodeString(arg : str, method : Method = Method.BASE64, coding : Coding = Coding.ASCII):
        # First convert to bytes array
        arg_b = arg.encode(coding)
        # Next encode as Base64
        enc_b = base64.b64encode(arg_b)
        # Finally convert back to string
        enc   = enc_b.decode(coding)
        return enc

    def decodeString(arg : str, method : Method = Method.BASE64, coding : Coding = Coding.ASCII):
        arg_b = arg.encode(coding)
        dec_b = base64.b64decode(arg_b)
        dec   = dec_b.decode(coding)
        return dec