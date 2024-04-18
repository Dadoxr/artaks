def get_abc_and_body(number):
    if number and len(number) == 11:
        try:
            abc, body = int(number[1:4]), int(number[4:])
        except Exception as e:
            abc, body = None, None
    else:
        abc, body = None, None
    return abc, body