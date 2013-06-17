##
# Copyright (C) 2013 Jessica T. (Tsyesika) <xray7224@googlemail.com>
# 
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
##

from models import AbstractModel

class Image(AbstractModel):
    
    TYPE = "image"

    # we need some methods to go grab the image for us.
    url = ""

    def __init__(self, url, *args, **kwargs):
        super(Image, self).__init__(self, *args, **kwargs)
        self.url = url

    def __repr__(self):
        return self.url

    def __str__(self):
        return self.__repr__()
