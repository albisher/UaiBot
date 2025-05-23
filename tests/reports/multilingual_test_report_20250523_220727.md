# UaiBot Multilingual Test Report

**Platform:** macOS Sequoia (15.5)  
**Date:** 2025-05-23 22:07:27  

## Summary

### Arabic
- **Passed:** 2/6 (33.3%)
- **Failed:** 4/6 (66.7%)

## Detailed Arabic Results

### Create file (AR): ❌ Failed

**Command:** `أنشئ ملف جديد باسم test_output_ar.txt واكتب فيه 'هذا ملف اختبار'`

**Reason:** No confirmation of file creation

**Output:**

```
Using Ollama model: gemma3:1b
Ollama initialized successfully
```
هذا ملف اختبار
```
```

---

### Read file (AR): ✅ Passed

**Command:** `اعرض محتوى الملف test_output_ar.txt`

**Reason:** Content reference found

---

### List files (AR): ❌ Failed

**Command:** `اعرض جميع الملفات في المجلد الحالي`

**Reason:** No file content found

**Output:**

```
Using Ollama model: gemma3:1b
Ollama initialized successfully
أعتقد أنك تريد عرض جميع الملفات في المجلد الحالي. 

لأساعدك بشكل أفضل، هل يمكنك إخباري:

*   **ما هو نظام التشغيل الخاص بك؟** (Windows, macOS, Linux)
*   **هل لديك أي برنامج معين تريد أن أساعدك في عرضه؟** (مثل Finder على macOS، أو File Explorer على Windows)
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

**Reason:** No confirmation of file deletion

**Output:**

```
Using Ollama model: gemma3:1b
Ollama initialized successfully
أنا آسف، لا يمكنني حذف الملف. أنا مساعد افتراضي ولست قادرًا على تنفيذ هذه المهمة.
```

---

