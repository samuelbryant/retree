# retree

retree is a tool designed to work with `re`, python's regex library to restructure regex output into a tree.

To be precise, it takes the output of a regex match (`re.Match`), which may contain several nested capture groups, and converts it into a tree (`retree.ReTree`) preserving the hierarchical group information.

This library is designed to be:
    - simple and easy to understand
    - well-tested
    - efficient

I developed this after discovering it wasn't already built-in to the `re` library.


## Basic usage

### Quick Examples

1. Display the result of regex match groups as a tree:
```
>>> regex     = 'Hello ([^ ]+), today is (([0-9]{4})-([0-9]{2})-([0-9]{2}))'
>>> test_case = 'Hello Maxwell, today is 2024-12-05'
>>> pattern = re.compile(regex)
>>> root = ReTree.pattern_match(pattern, test_case)
>>> root.display(show_index=False)
Hello Maxwell, today is 2024-12-05
  Maxwell
  2024-12-05
    2024
    12
    05
```
Can also display the original group indices:
```
>>> root.display(show_index=True)
0 Hello Maxwell, today is 2024-12-05
1   Maxwell
2   2024-12-05
3     2024
4     12
5     05
```

2. Interact with matched groups via a tree.
```
>>> regex     = 'Hello ([^ ]+), today is (([0-9]{4})-([0-9]{2})-([0-9]{2}))'
>>> test_case = 'Hello Maxwell, today is 2024-12-05'
>>> pattern = re.compile(regex)
>>> root = ReTree.pattern_match(pattern, test_case)
assert(root.text == test_case)
assert(root.children[0].text == 'Maxwell')
assert(root.children[1].text == '2024-12-05')
assert(root.children[1].children[0].text == '2024')
```

3. Apply functions by visiting tree nodes
```
>>> def print_node(node):
>>>    print('index = %d, depth = %d, text = %s' % (node.index, node.get_depth(), node.text))
>>>
>>> root.do_for_all(lambda x : print_node(x))
index = 0, depth = 3, text = Hello Maxwell, today is 2024-12-05
index = 1, depth = 1, text = Maxwell
index = 2, depth = 2, text = 2024-12-05
index = 3, depth = 1, text = 2024
index = 4, depth = 1, text = 12
index = 5, depth = 1, text = 05
```


### Comparison with Vanilla

**Vanilla Python**
A normal usage of python's `re` library may look like the following:
```
# In this example, we use regex to parse lines of log files which look like:
# 2024-12-05: <ERR>: This is an error message
date_regex = '(([0-9]{4})-([0-9]{1,2})-([0-9]{1,2}))'
type_regex = '<([^>]+)>'
mesg_regex = '(.*)'
regex     = '%s: %s: %s' % (date_regex, type_regex, mesg_regex)
test_case = '2024-12-05: <MSG>: This is a log message'

pattern = re.compile(regex)
match = pattern.match(test_case)

print(match.group(0)) # 2024-12-05: <MSG>: This is a log message
print(match.group(1)) # 2024-12-05
print(match.group(2)) # 2024
print(match.group(3)) # 12
print(match.group(4)) # 05
print(match.group(5)) # MSG
print(match.group(6)) # This is a log message
```

The problem is that there is no way to interact with this data hierarchically. We can only view it as a list where, for example, `2024` and `2024-12-05` have no formal relationship.

**With retree**
With the retree library we can convert this information into a tree:
```
import re, retree

# Same regex and test case as above
date_regex = '(([0-9]{4})-([0-9]{2})-([0-9]{2}))'
type_regex = '<([^>]+)>'
mesg_regex = '(.*)'
regex     = '%s: %s: %s' % (date_regex, type_regex, mesg_regex)
test_case = '2024-12-05: <MSG>: This is a log message'

pattern = re.compile(regex)
root = ReTree.pattern_match(pattern, test_case)

print(root)                           # 2024-12-05: <MSG>: This is a log message
print(root.children[0])               # 2024-12-05
print(root.children[0].children[0])   # 2024
print(root.children[0].children[1])   # 12
print(root.children[0].children[2])   # 05
print(root.children[1])               # MSG
print(root.children[2])               # This is a log message
```

