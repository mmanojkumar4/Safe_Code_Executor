

# Security Notes — Safe Code Executor 

---
## 1. Filesystem Isolation

### Test
```python
print(open("/etc/passwd").read())
````

### Result

The container printed its **own** `/etc/passwd` file, not the host system’s file.

### Meaning

* Docker containers have their **own filesystem**.
* They CANNOT access host files unless manually mounted.
* Good isolation but not full security boundary.

---

## 2. Read-Only Filesystem

### Test

```python
open("/tmp/hack.txt", "w").write("hello")
```

### Result

```
OSError: [Errno 30] Read-only file system
```

### Meaning

* Because of `--read-only`, the container cannot write anywhere.
* This prevents file-based attacks or persistence inside the container.

---

## 3. Read-Only Volume Mount

### Test

```python
open("/app/script.py", "w").write("hacked")
```

### Result

```
OSError: [Errno 30] Read-only file system
```

### Meaning

* The mounted script file is read-only (`:ro`).
* Prevents user code from modifying or escaping via mounted volumes.

---

## 4. Network Isolation

### Test

```python
import urllib.request
urllib.request.urlopen("https://google.com")
```

### Result

```
Temporary failure in name resolution
```

### Meaning

* Because of `--network none`, container has **no internet**.
* Prevents data exfiltration or malicious network requests.

---

## 5. Memory Isolation

### Test

```python
x = "a" * 1000000000
```

### Result

Container closed with **exit code 137**.

### Meaning

* Memory usage was limited with:

  ```
  --memory=128m
  --memory-swap=128m
  ```
* Prevents crashes or RAM-overflow attacks.

---

## 6. Timeout Protection

### Test

```python
while True:
    pass
```

### Result

```
Execution timed out after 10 seconds.
```

### Meaning

* The Python subprocess was killed automatically after 10 seconds.
* Prevents infinite loops and keeps the API responsive.

---

# Summary of Learnings

* Docker provides **process**, **filesystem**, and **network** isolation.
* With added limits (timeout, memory, read-only, no network), it becomes a safe sandbox.
* Docker alone is not a complete security boundary, but proper configuration makes it suitable for controlled code execution.




