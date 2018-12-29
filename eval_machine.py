# coding: utf-8

import sys
import numpy as np
import pandas as pd
from pandas.core.computation.ops import UndefinedVariableError
from functools import partial
from typing import Any, Union, Tuple




def _get_bool_masks(dct: dict, try_convert_types=True, prefix='is_', verbose_mode=False) -> dict:
    """ Получить булеву маску значения/массива значений """

    result = {}

    if dct:
        for k, v in dct.items():
            try:
                result["{0}{1}".format(prefix, k)] = v.astype(bool)

            except (ValueError, TypeError):
                if try_convert_types:
                    result["{0}{1}".format(prefix, k)] = v.astype(object).astype(bool)

                if verbose_mode:
                    print(
                        "Error convert numpy array to bool type for value <{0}> on key <{1}>... "
                        "It is possible to get an array with incorrect types (i.e <U11>)".format(v, k),
                        file=sys.stderr
                    )

    return result




def _eval_apply(
    expr: Union[dict, str, None],
    current_expr_deep: int = 1,
    expr_deep_limit: int = 5,
    onerror_value: Any = None,
    global_dict: Union[dict, None] = None,
    verbose_mode: bool = False

) -> Tuple[Union[dict, str], int]:

    """ Рекурсивная <eval> машина для выражений pandas\numpy

        :param expr: Выражение в строковом представлении или в виде условий {'IF': ..., 'THEN': ..., 'ELSE': ...}
        :param current_expr_deep: Текущая глубина рекурсии (вложенности условий)
        :param expr_deep_limit: Допустимая глубина рекурсии
        :param onerror_value: Значение при превышении глубины рекурсии
        :param global_dict: Глобальные переменные функции
        :param verbose_mode: Подробный вывод ошибок и предупреждений
    """

    if expr is None:
        if verbose_mode:
            print('###EVAL MACHINE ERROR### Expression is <None> - returning a default value: <{}>'.format(onerror_value), file=sys.stderr)
        result = onerror_value


    ### Принимаем <dict> как описание вложенной функции, а не конечное выражение для <eval>
    elif isinstance(expr, dict):
        current_expr_deep += 1
        if current_expr_deep >= expr_deep_limit:
            if verbose_mode:
                print('###EVAL MACHINE ERROR### Get recursion limit on expression: <{}>'.format(expr), file=sys.stderr)
            result = onerror_value
        else:
            _eval = partial(_eval_apply, current_deep=current_expr_deep, global_dict=global_dict)
            result, current_expr_deep = _eval(expr['THEN']) if _eval(expr['IF']) else _eval(expr['ELSE'])


    ### Иначе если <expr> - это строка, то интерпретируем это выражение
    else:
        current_expr_deep -= 1
        try:
            result = pd.eval(expr, global_dict=global_dict)
        except UndefinedVariableError as err:
            if verbose_mode:
                print('###EVAL MACHINE ERROR### Undefined variable error: <{}>'.format(err), file=sys.stderr)
            result = onerror_value
        except Exception as err:
            if verbose_mode:
                print('###EVAL MACHINE ERROR### Unexpected error: <{}>'.format(err), file=sys.stderr)
            result = onerror_value

    return result, current_expr_deep





def eval_apply_recursively(
    expr: Union[dict, str, None],
    expr_deep_limit: int = 5,
    global_dict: Union[dict, None] = None,
    create_bool_masks: bool = True,
    bool_masks_prefix: str = 'is_',
    verbose_mode: bool = False,
    onerror_value: Any = None,

) -> Any:

    """ Рекурсивная <eval> машина для векторизованных операций

        :param expr: Выражение в строковом представлении или в виде условий {'IF': ..., 'THEN': ..., 'ELSE': ...}
        :param expr_deep_limit: Допустимая глубина рекурсии
        :param global_dict: Глобальные переменные функции
        :param create_bool_masks: Сформировать булевы маски переменных ?
        :param verbose_mode: Подробный вывод ошибок и предупреждений
        :param create_bool_masks: Сформировать булевы маски переменных ?
        :param bool_masks_prefix: Префикс для булевых представлений переменных и массивов
        :param onerror_value: Значение при превышении глубины рекурсии
    """

    if create_bool_masks:
        global_dict_mask = _get_bool_masks(global_dict, prefix=bool_masks_prefix)
        global_dict.update(global_dict_mask)

    result, deep = _eval_apply(expr, current_expr_deep=1, expr_deep_limit=expr_deep_limit, onerror_value=onerror_value, global_dict=global_dict, verbose_mode=verbose_mode)

    return result





def test1():
    eval_expr = {
        'IF': 'is_x.any()',
        'THEN': {'IF': '~is_curr_row.A.any()', 'THEN': 'prev_row.B', 'ELSE': 'x'},
        'ELSE': 'x'
    }

    global_dict = {
        'x': np.array(['test']),
        'curr_row': pd.Series({'A': np.array(['note_1']), 'B': np.array(['note_2'])}),
        'prev_row': pd.Series({'A': np.array(['note_11']), 'B': np.array(['note_22'])}),
    }

    res = eval_apply_recursively(eval_expr, global_dict=global_dict, bool_masks_prefix='is_')
    print(res)




if __name__ == "__main__":
    test1()
