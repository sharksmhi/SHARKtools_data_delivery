#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2018 SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import tkinter as tk
import traceback
from pathlib import Path
from tkinter import filedialog
from tkinter import messagebox
import logging

import ctd_processing
import file_explorer
from sharkpylib.tklib import tkinter_widgets as tkw

from ..saves import SaveComponents

logger = logging.getLogger(__file__)


class StringVar:
    def __init__(self, id_string=None):
        self._id = id_string
        self._stringvar = tk.StringVar()

    def __call__(self, *args, **kwargs):
        return self._stringvar

    def set(self, value):
        self._stringvar.set(value)

    def get(self):
        return self._stringvar.get()


class PageCTD(tk.Frame):

    def __init__(self, parent, parent_app, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        # parent is the frame "container" in App. controller is the App class
        self.parent = parent
        self.parent_app = parent_app
        self._saves = SaveComponents('ctd')

        self._all_packs_in_source_directory = []
        self._selected_packs = []

        self._stringvars_meta = {}
        self._stringvars_path = {}
        self._stringvars_stat = {}
        self._stringvars_stat_all = {}

    @property
    def user(self):
        return self.parent_app.user

    def startup(self):
        self._build()
        self._add_to_save()
        self._on_select_local_dir()

    def _add_to_save(self):
        self._saves.add_components(*list(self._stringvars_path.values()))
        self._saves.add_components(*list(self._stringvars_meta.values()))
        self._saves.load()
        self._check_missing_paths()

    def _check_missing_paths(self):
        missing = []
        for name, stringvar in self._stringvars_path.items():
            string = stringvar.get().strip()
            if not string:
                missing.append(name)
            else:
                path = Path(string)
                if not path.exists():
                    stringvar.set('')
                    missing.append(name)
                    if name == 'local_root_dir':
                        self._all_packs_in_source_directory = []
        return missing

    def _get_paths(self):
        missing = self._check_missing_paths()
        paths = {}
        for name, stringvar in self._stringvars_path.items():
            if name in missing:
                continue
            paths[name] = Path(stringvar.get())
        return paths

    def _create_stringvars(self):
        self._stringvars_path['local_root_dir'] = StringVar('local_root_dir')
        self._stringvars_path['output_dir'] = StringVar('output_dir')
        self._stringvars_path['sharkweb_file'] = StringVar('sharkweb_file')

        self._stringvars_meta['mprog'] = StringVar('mprog')
        self._stringvars_meta['description'] = StringVar('description')
        self._stringvars_meta['contact'] = StringVar('contact')
        self._stringvars_meta['comment'] = StringVar('comment')

        self._stringvars_stat['.txt'] = tk.StringVar()
        self._stringvars_stat['.cnv'] = tk.StringVar()
        self._stringvars_stat['.hex'] = tk.StringVar()
        self._stringvars_stat['.hdr'] = tk.StringVar()
        self._stringvars_stat['.ros'] = tk.StringVar()
        self._stringvars_stat['.bl'] = tk.StringVar()
        self._stringvars_stat['.btl'] = tk.StringVar()
        self._stringvars_stat['.xmlcon'] = tk.StringVar()
        self._stringvars_stat['.con'] = tk.StringVar()
        self._stringvars_stat['.zip'] = tk.StringVar()
        self._stringvars_stat['.jpg'] = tk.StringVar()
        self._stringvars_stat['.png'] = tk.StringVar()
        self._stringvars_stat['.deliverynote'] = tk.StringVar()
        self._stringvars_stat['.metadata'] = tk.StringVar()
        self._stringvars_stat['.sensorinfo'] = tk.StringVar()

        self._stringvars_stat_all['.txt'] = tk.StringVar()
        self._stringvars_stat_all['.cnv'] = tk.StringVar()
        self._stringvars_stat_all['.hex'] = tk.StringVar()
        self._stringvars_stat_all['.hdr'] = tk.StringVar()
        self._stringvars_stat_all['.ros'] = tk.StringVar()
        self._stringvars_stat_all['.bl'] = tk.StringVar()
        self._stringvars_stat_all['.btl'] = tk.StringVar()
        self._stringvars_stat_all['.xmlcon'] = tk.StringVar()
        self._stringvars_stat_all['.con'] = tk.StringVar()
        self._stringvars_stat_all['.zip'] = tk.StringVar()
        self._stringvars_stat_all['.jpg'] = tk.StringVar()
        self._stringvars_stat_all['.png'] = tk.StringVar()
        self._stringvars_stat_all['.deliverynote'] = tk.StringVar()
        self._stringvars_stat_all['.metadata'] = tk.StringVar()
        self._stringvars_stat_all['.sensorinfo'] = tk.StringVar()

    def _build(self):
        self._create_stringvars()

        self._frame_paths = tk.LabelFrame(self, text='Sökvägar')
        self._frame_paths.grid(row=0, column=0, columnspan=3)

        self._frame_stat_all = tk.LabelFrame(self, text='Statistik (alla filer)')
        self._frame_stat_all.grid(row=1, column=0, rowspan=2)

        self._frame_files = tk.LabelFrame(self, text='Inkludera filer')
        self._frame_files.grid(row=1, column=1)

        self._frame_metadata = tk.LabelFrame(self, text='Information om leveransen')
        self._frame_metadata.grid(row=2, column=1)

        self._frame_stat = tk.LabelFrame(self, text='Statistik (valda filer)')
        self._frame_stat.grid(row=1, column=2, rowspan=2)

        tkw.grid_configure(self, nr_rows=3, nr_columns=3)
        
        self._build_path_frame()
        self._build_files_frame()
        self._build_stat_all_frame()
        self._build_stat_frame()
        self._build_metadata_frame()

    def _build_path_frame(self):
        frame = self._frame_paths
        opt = dict(width=30)
        grid = dict(padx=5, pady=5)
        r = 0
        tk.Button(frame, text='Lokal rotmapp (källmapp)', command=self._select_local_root_dir, **opt).grid(row=r, column=0, **grid)
        tk.Label(frame, textvariable=self._stringvars_path['local_root_dir']()).grid(row=r, column=1, **grid, sticky='w')
        r += 1
        tk.Button(frame, text='Exportmapp', command=self._select_output_dir, **opt).grid(row=r, column=0, **grid)
        tk.Label(frame, textvariable=self._stringvars_path['output_dir']()).grid(row=r, column=1, **grid, sticky='w')
        r += 1
        tk.Button(frame, text='Sökväg till SHARKweb-uttag (radformat)', command=self._select_sharkweb_file, **opt).grid(row=r, column=0, **grid)
        tk.Label(frame, textvariable=self._stringvars_path['sharkweb_file']()).grid(row=r, column=1, **grid, sticky='w')

        tkw.grid_configure(frame, nr_rows=r+1, nr_columns=1)

    def _build_files_frame(self):
        frame = self._frame_files
        props = dict(width=45)
        self._listbox_files = tkw.ListboxSelectionWidget(frame,
                                                         callback=self._on_select_files,
                                                         prop_items=props,
                                                         prop_selected=props,
                                                         row=0, column=0)

    def _build_stat_all_frame(self):
        frame = self._frame_stat_all
        grid = dict(padx=5, pady=2)
        r = 0
        for suffix, stringvar in self._stringvars_stat_all.items():
            tk.Label(frame, text=f'Antal {suffix}-filer:').grid(row=r, column=0, **grid, sticky='e')
            tk.Label(frame, textvariable=stringvar).grid(row=r, column=1, **grid, sticky='w')
            r += 1
        tkw.grid_configure(self, nr_rows=r, nr_columns=2)
        
    def _build_stat_frame(self):
        frame = self._frame_stat
        grid = dict(padx=5, pady=2)
        r = 0
        for suffix, stringvar in self._stringvars_stat.items():
            tk.Label(frame, text=f'Antal {suffix}-filer:').grid(row=r, column=0, **grid, sticky='e')
            tk.Label(frame, textvariable=stringvar).grid(row=r, column=1, **grid, sticky='w')
            r += 1
        tkw.grid_configure(self, nr_rows=r, nr_columns=2)

    def _build_metadata_frame(self):
        frame = self._frame_metadata
        grid = dict(padx=5, pady=2)
        r = 0
        svar = tk.StringVar()
        tk.Label(frame, text='Mätprogram').grid(row=r, column=0, **grid, sticky='e')
        tk.Entry(frame, textvariable=self._stringvars_meta['mprog'](), width=50).grid(row=r, column=1, **grid, sticky='w')
        svar.set('test')
        r += 1
        tk.Label(frame, text='Beskrivning').grid(row=r, column=0, **grid, sticky='e')
        tk.Entry(frame, textvariable=self._stringvars_meta['description'](), width=50).grid(row=r, column=1, **grid, sticky='w')
        r += 1
        tk.Label(frame, text='Kontaktperson').grid(row=r, column=0, **grid, sticky='e')
        ent = tk.Entry(frame, textvariable=self._stringvars_meta['contact'](), width=50)
        ent.grid(row=r, column=1, **grid, sticky='w')
        r += 1
        tk.Label(frame, text='Kommentar').grid(row=r, column=0, **grid, sticky='e')
        tk.Entry(frame, textvariable=self._stringvars_meta['comment'](), width=50).grid(row=r, column=1, **grid, sticky='w')
        r += 1
        self._intvar_overwrite = tk.IntVar()
        tk.Checkbutton(frame, text='Skriv över filer', variable=self._intvar_overwrite).grid(row=r, column=1, **grid, sticky='w')
        r += 1
        tk.Button(frame, text='Skapa leverans', command=self._create_delivery, bg='#6293e3').grid(row=r, column=0, columnspan=2, **grid, sticky='ew')

        tkw.grid_configure(frame, nr_rows=r+1, nr_columns=2)

    @property
    def overwrite(self):
        return bool(self._intvar_overwrite.get())

    def _create_delivery(self):
        missing = self._check_missing_paths()
        if 'local_root_dir' in missing:
            messagebox.showwarning('Skapa leverans', 'Kan inte skapa leverans. Källmapp saknas!')
            return
        if 'output_dir' in missing:
            messagebox.showwarning('Skapa leverans', 'Kan inte skapa leverans. Exportmap saknas!')
            return
        if not self._selected_packs:
            messagebox.showwarning('Skapa leverans', 'Kan inte skapa leverans. Inga filer valda!')
            return

        msg = self._check_selected_packs_content()
        if msg:
            logger.error(msg)
            if not messagebox.askyesno('Ofullständing information', msg):
                return
        output_dir = self._stringvars_path['output_dir'].get()
        metadata = self._get_metadata()

        logger.info(f'{output_dir=}')
        logger.info(f'{metadata=}')

        try:
            ctd_processing.create_dv_delivery_for_packages(self._selected_packs, output_dir, overwrite=self.overwrite, **metadata)
            messagebox.showinfo('Skapa leverans', 'Leverans har skapats!')
        except FileExistsError as e:
            messagebox.showerror('Skapa leverans', f'Fil finns redan: {e}')
        except:
            messagebox.showerror('Skapa leverans', f'Internt fel: {traceback.format_exc()}')
            raise

    def _get_metadata(self):
        meta = {}
        for key, svar in self._stringvars_meta.items():
            value = svar.get().strip()
            if not value:
                continue
            meta[key] = value
        return meta

    def _on_select_local_dir(self):
        directory = self._get_paths().get('local_root_dir')
        if not directory:
            return
        self._all_packs_in_source_directory = file_explorer.get_packages_in_directory(directory, exclude_directory='temp', as_list=True)
        logger.info(f'{ self._all_packs_in_source_directory=}')
        if not self._all_packs_in_source_directory:
            msg = f'inga fullständiga paket i rotkatalogen: {directory}'
            logger.warning(msg)
            messagebox.showwarning('Filer saknas', msg)
            return
        msg = self._check_all_packs_content()
        if msg:
            logger.warning(msg)
            messagebox.showwarning('Otillräcklig information', msg)
            return
        self._update_stat_all()
        self._update_listbox_files()

    def _on_select_files(self):
        selected_names = self._listbox_files.get_selected()
        keys = [name.split('.')[0] for name in selected_names]
        self._selected_packs = [pack for pack in self._all_packs_in_source_directory if pack.key in keys]
        self._update_stat()

    def _update_listbox_files(self):
        self._listbox_files.update_items()
        if not self._all_packs_in_source_directory:
            return
        file_names = []
        for pack in self._all_packs_in_source_directory:
            path = pack.get_file_path(suffix='.txt')
            if not path:
                continue
            file_names.append(path.name)
        self._listbox_files.update_items(file_names)

    @staticmethod
    def _get_statistics_for_packs(packs_list):
        if not packs_list:
            return
        nr_files = {}
        for pack in packs_list:
            for file in pack.files:
                nr_files.setdefault(file.suffix, 0)
                nr_files[file.suffix] += 1
        return dict(nr_files=nr_files)

    def _get_all_packs_statistics(self):
        return self._get_statistics_for_packs(self._all_packs_in_source_directory)

    def _get_packs_statistics(self):
        return self._get_statistics_for_packs(self._selected_packs)

    def _reset_stat_all(self):
        for stringvar in self._stringvars_stat_all.values():
            stringvar.set('')

    def _reset_stat(self):
        for stringvar in self._stringvars_stat.values():
            stringvar.set('')

    def _check_all_packs_content(self):
        missing_txt = []
        new_pack_list = []
        for pack in self._all_packs_in_source_directory:
            if not pack['txt']:
                missing_txt.append(pack.key)
                missing_txt.append(pack.key)
                continue
            new_pack_list.append(pack)
        self._all_packs_in_source_directory = new_pack_list
        if missing_txt:
            return f'Det saknas standardformat för: {", ".join(missing_txt)}. Dessa kommer inte att inkluderas'

    def _check_selected_packs_content(self):
        missing_sensorinfo = []

    def _update_stat_all(self):
        self._reset_stat_all()
        stat = self._get_all_packs_statistics()
        for suffix, nr in stat['nr_files'].items():
            self._stringvars_stat_all[suffix].set(str(nr or 0))

    def _update_stat(self):
        self._reset_stat()
        stat = self._get_packs_statistics()
        for suffix, nr in stat['nr_files'].items():
            self._stringvars_stat[suffix].set(str(nr or 0))

    def _select_local_root_dir(self):
        directory = filedialog.askdirectory(title='Välj lokal rotmapp')
        if not directory:
            return
        self._stringvars_path['local_root_dir'].set(directory)
        self._on_select_local_dir()

    def _select_output_dir(self):
        directory = filedialog.askdirectory(title='Välj exportmapp')
        if not directory:
            return
        self._stringvars_path['output_dir'].set(directory)

    def _select_sharkweb_file(self):
        file = filedialog.askopenfilename(title='Välj SHARKweb-fil (radformat)')
        if not file:
            return
        self._stringvars_path['sharkweb_file'].set(file)

    def close(self):
        self._saves.save()

    def update_page(self):
        print('UPDATE')

