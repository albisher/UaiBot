# File Operations Commands

## English Commands

### Create Files
- create file [filename] with content '[content]'
- make a new file named [filename] containing '[content]'
- create a file called [filename] with the text '[content]'
- create a new file [filename] and write '[content]' to it
- make file [filename] with content '[content]'
- create [filename] with '[content]' in it
- create a file [filename] in the folder [path] with content '[content]'
- make a new file inside [path] named [filename] containing '[content]'

### Read Files
- read file [filename]
- show me the contents of [filename]
- display the content of [filename]
- open file [filename]
- what's in [filename]
- show [filename]
- read the file [filename] in folder [path]
- display contents of [filename] in directory [path]

### Write/Update Files
- write '[content]' to [filename]
- update [filename] with '[content]'
- modify [filename] to contain '[content]'
- change [filename] to have '[content]'
- write '[content]' to [filename] in folder [path]
- update [filename] in directory [path] with '[content]'

### Append Content
- append '[content]' to [filename]
- add '[content]' to [filename]
- add the text '[content]' to [filename]
- append '[content]' to [filename] in folder [path]
- add '[content]' to [filename] in directory [path]

### Delete Files
- delete file [filename]
- remove [filename]
- delete the file [filename]
- remove file [filename] from folder [path]
- delete [filename] from directory [path]

### Search Files
- search for files containing '[pattern]'
- find files with '[pattern]' in the name
- look for files named '[pattern]'
- search for '[pattern]' in folder [path]
- find files with '[pattern]' in directory [path]

### List Files
- list files in [path]
- show all files in [path]
- what files are in [path]
- list contents of [path]
- show files in directory [path]

## Arabic Commands

### إنشاء الملفات
- إنشاء ملف [filename] بالمحتوى '[content]'
- إنشاء ملف جديد باسم [filename] يحتوي على '[content]'
- إنشاء ملف [filename] مع النص '[content]'
- إنشاء ملف جديد [filename] وكتابة '[content]' فيه
- إنشاء ملف [filename] في المجلد [path] بالمحتوى '[content]'
- إنشاء ملف جديد داخل [path] باسم [filename] يحتوي على '[content]'

### قراءة الملفات
- قراءة ملف [filename]
- عرض محتوى [filename]
- فتح ملف [filename]
- ما هو محتوى [filename]
- عرض [filename]
- قراءة ملف [filename] في المجلد [path]
- عرض محتوى [filename] في المجلد [path]

### كتابة/تحديث الملفات
- كتابة '[content]' في [filename]
- تحديث [filename] بمحتوى '[content]'
- تعديل [filename] ليتضمن '[content]'
- تغيير [filename] ليحتوي على '[content]'
- كتابة '[content]' في [filename] في المجلد [path]
- تحديث [filename] في المجلد [path] بمحتوى '[content]'

### إضافة محتوى
- إضافة '[content]' إلى [filename]
- إلحاق '[content]' بـ [filename]
- إضافة النص '[content]' إلى [filename]
- إضافة '[content]' إلى [filename] في المجلد [path]
- إلحاق '[content]' بـ [filename] في المجلد [path]

### حذف الملفات
- حذف ملف [filename]
- إزالة [filename]
- حذف الملف [filename]
- إزالة ملف [filename] من المجلد [path]
- حذف [filename] من المجلد [path]

### البحث عن الملفات
- البحث عن ملفات تحتوي على '[pattern]'
- العثور على ملفات باسم '[pattern]'
- البحث عن '[pattern]' في المجلد [path]
- العثور على ملفات باسم '[pattern]' في المجلد [path]

### عرض قائمة الملفات
- عرض ملفات المجلد [path]
- عرض جميع الملفات في [path]
- ما هي الملفات الموجودة في [path]
- عرض محتويات المجلد [path]
- عرض الملفات في المجلد [path]

## Examples

### English Examples
1. Create a new file:
   ```
   create file test.txt with content 'Hello World'
   ```

2. Read a file:
   ```
   read file test.txt
   ```

3. Update a file:
   ```
   write 'New content' to test.txt
   ```

4. Search for files:
   ```
   search for files containing 'test'
   ```

### Arabic Examples
1. إنشاء ملف جديد:
   ```
   إنشاء ملف test.txt بالمحتوى 'مرحبا بالعالم'
   ```

2. قراءة ملف:
   ```
   قراءة ملف test.txt
   ```

3. تحديث ملف:
   ```
   كتابة 'محتوى جديد' في test.txt
   ```

4. البحث عن ملفات:
   ```
   البحث عن ملفات تحتوي على 'test'
   ```

## Notes
- All file paths should be relative to the current working directory unless specified otherwise
- File names should not contain special characters except for dots and underscores
- Content should be properly escaped when containing quotes
- Directory paths should use forward slashes (/) even on Windows
- Commands are case-insensitive
- Arabic commands should use proper Arabic punctuation marks
- File operations should handle both text and binary files appropriately
- Error messages should be clear and helpful in both languages 