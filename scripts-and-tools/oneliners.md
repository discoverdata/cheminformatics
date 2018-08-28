# Useful one liners

## Sort a file (file1) based on patterns in a different file (file2)

```bash
while read pattern; do frep "${pattern}" file_1 >> sorted_file1; done < file2
```
