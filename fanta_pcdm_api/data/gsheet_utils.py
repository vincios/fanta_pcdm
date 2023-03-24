# Utilities to load data from Google Sheets
import time
from typing import Any

import gspread
import gspread.utils


def get_client(credentials) -> gspread.Client:
    return gspread.service_account_from_dict(credentials)


def grid_bounds_by_a1(name: str, sheet_id=None):
    """
    Converts a range defined in A1 notation to a dict representing a `GridRange`_.
    All indexes are 1-based. Indexes are half open, e.g. the start
    index is inclusive and the end index is exclusive: [startIndex, endIndex).
    Missing indexes indicate the range is unbounded on that side.

    This is similar to ``gspread.utils.a1_range_to_grid_range` but with 1-based indexes
    """
    grid_range = gspread.utils.a1_range_to_grid_range(name, sheet_id)
    return {k: v + 1 for k, v in grid_range.items()}


def cells_group_by_row(cells: list[gspread.Cell]) -> list[list[gspread.Cell]]:
    """
    Group a list of cells in a list of lists of cells, where in each list all cells have the same row number
    :param cells: list of cells to group
    :return: list of lists of cells, grouped by cell row number
    """
    row_numbers = sorted(set(map(lambda cell: cell.row, cells)))
    return [sorted([cell for cell in cells if cell.row == row], key=lambda x: x.col) for row in row_numbers]


class WorksheetLoader(object):
    _sheet_key: str
    _client: gspread.Client
    _sheet: gspread.Spreadsheet | None
    _worksheet: gspread.Worksheet | None
    _cells: list[gspread.Cell] | None

    _table_mode: bool

    def __init__(self, client: gspread.Client, sheet_key: str = None, sheet: gspread.Spreadsheet = None):
        """
        Utility class to work with a worksheet.

        You can pass the sheet_key and the sheet will be loaded automatically OR you can pass an already loaded sheet
        :param client: gspread Client
        :param sheet_key: OPTIONAL id of the spreadsheet to load
        :param sheet: OPTIONAL loaded gspread spreadsheet
        """
        self._client = client
        self._sheet_key = sheet_key
        self._sheet = sheet
        self._worksheet = None
        self._cells = None
        self._table_mode = False

    def _assert_table_mode(self, request: bool) -> bool:
        """
        Assert whether the worksheet is in table mode.

        If ``request`` is True, this method will throw a RuntimeError if the worksheet IS NOT in table mode.

        If ``request`` is False, this method il throw a RuntimeError if the IS in table mode
        :param request: whether the worksheet must be in table mode or not
        :return: True if request match the table_mode status
        """
        if request and not self._table_mode:
            raise RuntimeError("The sheet must be in table mode")
        elif not request and self._table_mode:
            raise RuntimeError("The sheet must not be in table mode")

        return True

    def _assert_sheet_loaded(self) -> bool:
        if not self._worksheet:
            raise RuntimeError("No worksheet loaded. Maybe you forgot to call load_worksheet()?")
        return True

    def load_worksheet(self, worksheet_title, table_mode: bool = False):
        self._table_mode = table_mode

        if not self._sheet and self._sheet_key:
            print(worksheet_title, "load spreadsheet")
            # time.sleep(0.5)
            self._sheet = self._client.open_by_key(self._sheet_key)
        else:
            raise ValueError("Neither sheet nor sheet_id provided")

        if self._worksheet:
            self._worksheet = None
            self._cells = None

        self._worksheet = self._sheet.worksheet(worksheet_title)

        # in table mode we don't need cells, instead we can use the get_all_records method
        if not self._table_mode:
            print(worksheet_title, "load cells")
            time.sleep(0.5)
            self._cells = self._worksheet.get_all_cells()

    def as_records(self) -> dict:
        """
        Return all rows in the table as records (list of dicts of header-value pairs)
        :return: all rows as records
        """
        self._assert_sheet_loaded()
        self._assert_table_mode(True)
        print(self._worksheet.title, "load records")
        # time.sleep(0.5)
        return self._worksheet.get_all_records()

    def get_cells(self, range_str: str = None, only_values: bool = False) -> list[gspread.Cell]:
        """
        Get all cells in a range written in a1 format. If no range is provided, returns all cells
        :param range_str: range string in a1 format
        :param only_values: return cells values instead of cells
        :return:
        """
        self._assert_sheet_loaded()
        self._assert_table_mode(False)

        if not range_str:
            return self._cells

        grid_range = grid_bounds_by_a1(range_str)
        row_offset = grid_range.get("startRowIndex", 1)
        column_offset = grid_range.get("startColumnIndex", 1)
        last_row = grid_range.get("endRowIndex", self._worksheet.row_count + 1)
        last_column = grid_range.get("endColumnIndex", self._worksheet.col_count + 1)

        return [
            cell.value if only_values else cell
            for cell in self._cells
            if row_offset <= cell.row < last_row
            and column_offset <= cell.col < last_column
        ]

    def get_values(self, range_str: str = None, by_row: bool = False) -> list[Any] | list[list[Any]]:
        """
        Get all values in a range written in a1 format. If no range is provided, returns all cells.

        If ``by_row`` is False, equivalent to ``get_cells(range_str, only_values=True)``.

        :param range_str: range string in a1 format
        :param by_row: returns a list of lists, where values are grouped by row and ordered by
        :return:
        """
        return self.get_cells(range_str, only_values=True) if not by_row \
            else [[cell.value for cell in row_cells] for row_cells in cells_group_by_row(self.get_cells(range_str))]

    def get_cell(self, address: str) -> gspread.Cell | None:
        """
        Return a single cell, given an address in a1 format
        :param address: a1 format cell address
        :return:
        """
        cell = self.get_cells(address)
        if len(cell) > 1:
            raise ValueError("Address returned not a single cell. Maybe is a range?")

        return None if len(cell) == 0 else cell[0]

    def get_value(self, address: str) -> Any | None:
        """
        Return a single value, given an address in a1 format
        :param address: a1 format cell address
        :return:
        """
        values = self.get_values(address)
        if len(values) > 1:
            raise ValueError("Address returned not a single value. Maybe is a range?")

        return None if len(values) == 0 else values[0]


if __name__ == "__main__":
    sheet_id = "1wt-PvS1Br0bE79-eQuZyJNa-RUo3SHdyMvzrekJQ7X4"
    rrange = "1:3"
    gc = gspread.service_account(filename="../../google_credentials.json")
    _sheet = gc.open_by_key(sheet_id)
    worksheet = _sheet.worksheet("Squadre")

    wl = WorksheetLoader(gc, sheet_id)
    wl.load_worksheet("Squadre")

    a1c3 = wl.get_cells(rrange)
    print(cells_group_by_row(a1c3))
    print(wl.get_values(rrange, by_row=True))
    print(worksheet.get_values(rrange))
