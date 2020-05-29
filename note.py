#!/usr/local/bin/python3.8






# 컨벤션 : 함수로 감싸고 결합을 이뤄야 좋은 코드이다. 함수를 안 썼기 때문에 전부 글로벌이 됐다. 

__main__ 형태는 마지막에 들어간다. 
   main()        # 덕지덕지 들어가던 내용들은 main() 함수를 만들고 그 안에 넣는 게 좋다. 
   
db 업로드 부분도 함수로 만들자 


import 할 때 내장 라이브러리와 외장 라이브러리는 구분해서 사용한다  (이것도 컨벤션)
생각보다 컨벤션이 많이 중요하다 

코드 리뷰는 정말 중요하다
앞으로 나아갈 수 있는 길을 열어주니 소스를 자주 공개하고 개선방향을 지속적으로 찾는다.



# PEP8 -- Style Guide for Python
스타일 가이드는 일관성에 관한 것이다. 
모듈 또는 기능 내에서 일관성은 가장 중요하다. 

Indentation (들여쓰기) 
들였기 레벨당 4개의 공백을 사용한다.
이어지는 들여쓰기를 할 때에는 시작을 구분하는 분리 문자와 일치하게 정렬한다.

# Aligned with opening delimiter.
# Correct !!
foo = long_func(var_one, var_two, 
                var_three, var_four)

def long_func2 (
    var_one, var_two, var_three,
    var_four) :
    print(var_one)

foo2 = long_func3 (
    var_one, var_two,
    var_three, var_four)

my_list = [
    1, 2, 3,
    4, 5, 6
]
result = some_func_that_takes_arguments (
    'a', 'b', 'c',
    'd', 'e', 'f',
)

탭 또는 공백
공백이 선호되는 들여쓰기 방법이다.
탭은 이미 탭으로 들여쓰기된 코드와 일관성을 유지하기 위해서만 사용해야 한다.
Python3 에서는 들여쓰기를 위해 탭과 공백을 혼합하여 사용할 수 없다.

최대 라인 길이
모든 줄을 최대 79자로 제한한다 (또는 99자까지도 늘려 쓴다)
편집기 창 너비를 제한하면 여러 파일을 나란히 열 수 있으며 인접한 열에 두 버전을 표시하는 코드 검토 도구를 사용할 때도 잘 작동한다.
파이썬 표준 라이브러리는 보수적이며 줄을 79자로 제한 필요하다. docstrings / comments는 72로 제한. 



이진 연산자 전후의 줄바꿈
# 맞음 :
피연산자와 연산자를 쉽게 일치시킬 수 있습니다.
수입 = (총액
          + taxable_interest
          + (배당금-유자격 배당금)
          -ira_deduction
          -student_loan_interest)


빈 줄
두 개의 빈 줄로 최상위 함수 및 클래스 정의를 둘러싼다.
클래스 내부의 메소드 정의는 한 줄씩 띄어쓴다.
여분의 빈 줄을 사용하여 관련 기능 그룹을 분리할 수 있다. 
파이썬은 

