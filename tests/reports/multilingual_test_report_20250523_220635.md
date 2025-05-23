# UaiBot Multilingual Test Report

**Platform:** macOS Sequoia (15.5)  
**Date:** 2025-05-23 22:06:35  

## Summary

### Arabic
- **Passed:** 1/6 (16.7%)
- **Failed:** 5/6 (83.3%)

## Detailed Arabic Results

### Create file (AR): ❌ Failed

**Command:** `أنشئ ملف جديد باسم test_output_ar.txt واكتب فيه 'هذا ملف اختبار'`

**Reason:** Error found in output

**Output:**

```
Using Ollama model: gemma3:1b
Ollama initialized successfully
Error: VALIDATION_ERROR: Invalid command structure
```

---

### Read file (AR): ❌ Failed

**Command:** `اعرض محتوى الملف test_output_ar.txt`

**Reason:** Error found in output

**Output:**

```
Using Ollama model: gemma3:1b
Ollama initialized successfully
Error: VALIDATION_ERROR: Invalid command structure
```

---

### List files (AR): ❌ Failed

**Command:** `اعرض جميع الملفات في المجلد الحالي`

**Reason:** No file content found

**Output:**

```
Using Ollama model: gemma3:1b
Ollama initialized successfully
أعتقد أنك تقصد عرض جميع الملفات في المجلد الحالي. 

لأساعدك بشكل أفضل، هل يمكنك إخباري:

*   **ما هو نظام التشغيل الخاص بك؟** (Windows, macOS, Linux, Android, iOS)
*   **هل تريد عرض الملفات بشكل عام أم فقط الملفات التي تسمى بـ .txt؟** (أو أي نوع آخر من الملفات)
```

---

### System info (AR): ❌ Failed

**Command:** `ما هو نظام التشغيل الذي أستخدمه؟`

**Reason:** No OS information found

**Output:**

```
Using Ollama model: gemma3:1b
Ollama initialized successfully
أنا نموذج لغوي كبير، تم تدريبي بواسطة جوجل.
```

---

### Disk space (AR): ✅ Passed

**Command:** `أظهر المساحة المتاحة على القرص`

**Reason:** Available space mentioned

---

### Delete file (AR): ❌ Failed

**Command:** `احذف الملف test_output_ar.txt`

**Reason:** Error found in output

**Output:**

```
Using Ollama model: gemma3:1b
Ollama initialized successfully
Error: VALIDATION_ERROR: Invalid command structure
```

---

