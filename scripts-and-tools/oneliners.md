# Useful one liners

## Sort a file (here fileName1) based on patterns in a different file (here fileName2)

```bash
while read pattern; do fgrep "${pattern}" fileName1 >> sorted_fileName1; done < fileName2
```

## Print the next line from the matching pattern

```bash
sed -n '/PATTERN/{n;p}' fileName 
```

## Set operations

### Get the intersection of two files (e.g. common ids in file1 and ids in file2)

```bash
grep -f fileName1 fileName2
```

### Get the values in file2 not in file1

```bash
grep -vf fileName1 fileName2
```
