# Fleet Protocol v2 HTTP API 
# Copyright (C) 2023 BringAuto s.r.o.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import sys
sys.path.append("server")


from server.fleetv2_http_api.__main__ import main as orig_main


def main()->None:
    orig_main()


if __name__ == '__main__':
    print("\n\nStarting the server\n\n")
    main()
