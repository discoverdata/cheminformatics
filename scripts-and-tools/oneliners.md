# Useful one liners

## Sort a file (here fileName1) based on patterns in a different file (here fileName2)

```bash
while read pattern; do fgrep "${pattern}" fileName1 >> sorted_fileName1; done < fileName2
```

## Print the next line from the matching pattern

```bash
sed -n '/PATTERN/{n;p}' fileName 
```

OR

1 line after the pattern match

```bash
grep -A1 'pattern' fileName
```

1 line before the pattern match

```bash
grep -B1 'pattern' fileName
```

## Set operations

### Get the intersection of two files (e.g. common ids in file1 and ids in file2)

```bash
grep -Fx -f fileName1 fileName2
```

### Get the values in file2 not in file1

```bash
grep -vf fileName1 fileName2
```

## Others

### Remove empty lines in vi editor
```bash
:g/^$/d
```

### Define tab as delimiter in bash cut command and remove the first column

```bash
cut -d$'\t' -f 2-
```

### Keep job running even after logging out

CTRL-Z
bg
disown %1


### When the process was started

```bash
ps -ef

OR

ps aux
```

### Elapsed time since the process (eg grep for a perl process)was started 

```bash
ps -eo pid,cmd,etime | grep 'perl'

OR
 
ps axo pid,cmd,etime | grep 'perl'
```
