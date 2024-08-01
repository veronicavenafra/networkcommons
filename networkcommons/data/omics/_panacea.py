#!/usr/bin/env python

#
# This file is part of the `networkcommons` Python module
#
# Copyright 2024
# Heidelberg University Hospital
#
# File author(s): Saez Lab (omnipathdb@gmail.com)
#
# Distributed under the GPLv3 license
# See the file `LICENSE` or read a copy at
# https://www.gnu.org/licenses/gpl-3.0.txt
#

"""
RNA-Seq data from the 'Pancancer Analysis of Chemical Entity Activity'
resource.
"""

from __future__ import annotations

__all__ = ['panacea_experiments', 'panacea_datatypes', 'panacea_tables']

import pandas as pd
import os
import urllib.parse

from . import _common

from networkcommons import _conf


def panacea_experiments(update=True) -> pd.DataFrame:
    """
    Table describing the experiments (drug-cell combinations) contained
    in the Panacea dataset.

    Returns:
        Data frame with all drug-cell line combinations
    """

    path = os.path.join(_conf.get('pickle_dir'), 'panacea_exps.pickle')

    if update or not os.path.exists(path):

        baseurl = urllib.parse.urljoin(_common._baseurl(), 'panacea')

        file_legend = pd.read_csv(baseurl + '/panacea__metadata.tsv', sep='\t')

        file_legend[['cell', 'drug']] = file_legend['group'].str.split('_', expand=True)
        file_legend.drop(columns='sample_ID', inplace=True)
        file_legend.drop_duplicates(inplace=True)
        file_legend.reset_index(drop=True, inplace=True)

        file_legend.to_pickle(path)

    else:

        file_legend = pd.read_pickle(path)

    return file_legend


def panacea_datatypes() -> pd.DataFrame:
    """
    Table describing the available data types in the Panacea dataset.

    Returns:
        Data frame with all data types.
    """

    return pd.DataFrame({
        'type': ['countdata', 'metadata'],
        'description': ['RNA-Seq raw counts', 'Metadata containing sample name and group'],
    })



def panacea_tables(cell_line=None, drug=None, type='countdata'):
    """
    One table of countdata and one table of metadata from Panacea.

    Args:
        cell_line:
            Name of the cell line(s). For a complete list see `panacea_experiments()`.
        drug:
            Name of the drug(s). For a complete list see `panacea_experiments()`.
        type:
            Type of data. For a complete list see `panacea_datatypes()`.

    Returns:
        tuple[pd.DataFrame]: Two data frames: counts and meta data.
    """

    df_meta = _common._open(
        _common._commons_url('panacea', table='metadata'),
        df = {'sep': '\t'},
    )

    df_meta[['cell', 'drug']] = df_meta['group'].str.split('_', expand=True)

    if isinstance(cell_line, str):
        cell_line = [cell_line]

    if isinstance(drug, str):
        drug = [drug]

    if cell_line is not None:
        df_meta = df_meta[df_meta['cell'].isin(cell_line)]

    if drug is not None:
        df_meta = df_meta[df_meta['drug'].isin(drug)]

    df_count = _common._open(
        _common._commons_url('panacea', table='countdata'),
        df={'sep': '\t'},
    )

    subset_cols = df_meta['sample_ID'].tolist()
    df_count = df_count.loc[:, ['gene_symbol'] + subset_cols]

    return df_count, df_meta

    return df_count, df_meta
