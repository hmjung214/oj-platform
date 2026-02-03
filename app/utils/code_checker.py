import ast

def detect_hardcoding(code: str, expected_outputs) -> bool:
    """
    - expected_outputs: 정답 문자열의 리스트 (각 테스트케이스 정답)
    - 입력 함수 미사용, print만 있을 때, 정답 생성하는 모든 리터럴/연산도 탐지
    """

    try:
        tree = ast.parse(code)
        found_input = False
        found_print = False

        def value_matches_any(val):
            sval = str(val).strip()
            for eo in expected_outputs:
                if sval == eo.strip() or eo.strip() in sval:
                    return True
            return False

        for node in ast.walk(tree):
            # 입력 함수 사용 체크 (input, sys.stdin, fileinput)
            if isinstance(node, ast.Call) and hasattr(node.func, "id") and node.func.id == "input":
                found_input = True
            if isinstance(node, ast.Attribute):
                if node.attr in ["stdin", "read", "readline"]:
                    found_input = True
            if isinstance(node, ast.ImportFrom) and node.module and "fileinput" in node.module:
                found_input = True

            # print 함수/정답 리터럴만 있는지 체크
            if isinstance(node, ast.Call) and hasattr(node.func, "id") and node.func.id == "print":
                found_print = True
                for arg in node.args:
                    # print(정답 리터럴)
                    if isinstance(arg, ast.Constant) and value_matches_any(arg.value):
                        return True
                    # print(연산 결과)
                    if isinstance(arg, (ast.BinOp, ast.UnaryOp)):
                        # 연산이 정답 만드는지 계산
                        try:
                            v = eval(compile(ast.Expression(arg), filename="", mode="eval"))
                            if value_matches_any(v):
                                return True
                        except Exception:
                            pass

            # f-string, JoinedStr
            if isinstance(node, ast.JoinedStr):
                s = ""
                for value in node.values:
                    if isinstance(value, ast.FormattedValue):
                        try:
                            v = eval(compile(ast.Expression(value.value), filename="", mode="eval"))
                            s += str(v)
                        except Exception:
                            pass
                    elif isinstance(value, ast.Constant):
                        s += str(value.value)
                if value_matches_any(s):
                    return True

            # 숫자/문자 리터럴(정답)
            if isinstance(node, ast.Constant):
                if value_matches_any(node.value):
                    return True

            # 해시 함수 등
            if isinstance(node, ast.Call):
                if hasattr(node.func, "id") and node.func.id == "hash":
                    return True

        # 입력 함수 없이 print만 있으면 하드코딩(입력 미사용)
        if not found_input and found_print:
            return True

    except Exception as e:
        print("detect_hardcoding error:", e)
        return False

    return False
