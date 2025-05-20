# UaiBot Multilingual Test Report

**Platform:** Ubuntu 24.04.2 LTS 24.04.2 LTS (Noble Numbat)  
**Date:** 2025-05-20 11:34:05  

## Summary

### Arabic
- **Passed:** 4/6 (66.7%)
- **Failed:** 2/6 (33.3%)

## Detailed Arabic Results

### Create file (AR): ✅ Passed

**Command:** `أنشئ ملف جديد باسم test_output_ar.txt واكتب فيه 'هذا ملف اختبار'`

**Reason:** File creation confirmed

---

### Read file (AR): ✅ Passed

**Command:** `اعرض محتوى الملف test_output_ar.txt`

**Reason:** File content found

---

### List files (AR): ❌ Failed

**Command:** `اعرض جميع الملفات في المجلد الحالي`

**Reason:** No file content found

**Output:**

```
Using Ollama model: gemma3:1b
Ollama initialized successfully
Executing with shlex: ['ls', '-l']
[38;5;244m🤔 Thinking...
┌───────────────────────────────────────────────┐
│ 🤖 Processing your request: 'اعرض جميع الملفات في المجلد الحالي' │
│                                               │
│ I'm thinking about how to best handle this... │
│ Analyzing the intent of your request...       │
│ Checking if I can map this to a system command... │
└───────────────────────────────────────────────┘[0m

[1;38;5;33m📌 I'll execute this command:[0m ls -l

[38;5;34m✅ Result:[0m
total 244
drwxrwxr-x 2 a a  4096 May 15 11:20 audio
drwxrwxr-x 7 a a  4096 May 19 12:58 backup
drwxrwxr-x 3 a a  4096 May 20 08:24 command_processor
-rw-rw-r-- 1 a a     0 May 20 07:01 command_processor.py
-rw-rw-r-- 1 a a  2870 May 18 06:58 COMMERCIAL_LICENSE
drwxrwxr-x 2 a a  4096 May 20 08:31 config
drwxrwxr-x 3 a a  4096 May 20 07:01 core
-rw-rw-r-- 1 a a    28 May 20 07:01 custom_note.txt
drwxrwxr-x 3 a a  4096 May 19 12:50 demo
drwxrwxr-x 3 a a  4096 May 18 06:59 device_manager
drwxrwxr-x 2 a a  4096 May 20 11:26 docs
drwxrwxr-x 3 a a  4096 May 20 07:01 examples
drwxrwxr-x 2 a a  4096 May 20 07:01 findings
drwxrwxr-x 2 a a  4096 May 20 11:26 fix
drwxrwxr-x 4 a a  4096 May 20 07:32 gui
-rw-rw-r-- 1 a a   183 May 18 06:58 __init__.py
drwxrwxr-x 3 a a  4096 May 19 12:57 input_control
-rw-rw-r-- 1 a a  2714 May 18 07:40 LICENSE
-rw-rw-r-- 1 a a   378 May 18 06:58 license_key.json.template
drwxrwxr-x 2 a a  4096 May 20 08:38 log
drwxrwxr-x 2 a a  4096 May 20 07:32 logs
-rwxrwxr-x 1 a a 37980 May 20 10:58 main.py
drwxrwxr-x 2 a a  4096 May 20 07:01 master
drwxrwxr-x 8 a a  4096 May 19 12:57 platform_uai
drwxrwxr-x 2 a a  4096 May 18 11:54 __pycache__
-rw-rw-r-- 1 a a  3688 May 20 07:09 README.md
-rw-rw-r-- 1 a a  4720 May 18 06:58 README.md.new
drwxrwxr-x 2 a a  4096 May 19 07:45 reference
-rw-rw-r-- 1 a a  2129 May 20 07:04 requirements.txt
drwxrwxr-x 3 a a  4096 May 20 07:01 screen_handler
drwxrwxr-x 2 a a  4096 May 18 06:58 src
-rwxrwxr-x 1 a a  2208 May 18 06:58 start_uaibot.py
drwxrwxr-x 3 a a  4096 May 20 07:01 terminal_commands
drwxrwxr-x 6 a a  4096 May 20 07:42 test_files
-rw-rw-r-- 1 a a    27 May 20 11:33 test_output_ar.txt
drwxrwxr-x 7 a a  4096 May 20 11:07 tests
drwxrwxr-x 2 a a  4096 May 20 11:16 todo
-rw-rw-r-- 1 a a 42568 May 19 13:22 uaibot.log
drwxrwxr-x 2 a a  4096 May 19 06:13 usb
drwxrwxr-x 2 a a  4096 May 18 06:58 usb_handler
drwxrwxr-x 3 a a  4096 May 20 07:01 utils
```

---

### System info (AR): ✅ Passed

**Command:** `ما هو نظام التشغيل الذي أستخدمه؟`

**Reason:** OS information found

---

### Disk space (AR): ✅ Passed

**Command:** `أظهر المساحة المتاحة على القرص`

**Reason:** Available space mentioned

---

### Delete file (AR): ❌ Failed

**Command:** `احذف الملف test_output_ar.txt`

**Reason:** Empty output

**Output:**

```
(No output)
```

**Errors:**

```
Command timed out after 30 seconds
```

---

