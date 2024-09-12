# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

from . import gui
from .app import App


INFO = dict(title='Data delivery',
            users_directory='users',
            sub_pages=[dict(name='PageCTD',
                            title='CTD')],
            user_page_class='PageUser')  # Must match name in ALL_PAGES in main app

USER_SETTINGS = []