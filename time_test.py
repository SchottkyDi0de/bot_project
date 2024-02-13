def narcissistic(value: int) -> bool:
    str_val = str(value)
    val_len = len(str_val)
    summ_of_elements = 0
    
    for i in str_val:
        summ_of_elements += int(i) ** val_len
        
    print(summ_of_elements)
        
    if summ_of_elements == value:
        return True
    
    return False

print(narcissistic(153))