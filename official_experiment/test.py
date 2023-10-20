test_list = "suc, nacl_l, none, none"
print(test_list)

new_list = test_list.split(", ")

# Format the items with double quotes and join them into a string
formatted_list = ', '.join(['"{}"'.format(item) for item in new_list])

# Add square brackets around the formatted list
formatted_list = "[" + formatted_list + "]"

print(formatted_list)