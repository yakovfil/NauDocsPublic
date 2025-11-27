Конфигурация менеджера скриптов
================================
.. _script_manager_doc:

В Nau Engine скрипты играют ключевую роль в реализации игровой логики. `ScriptManager <https://github.com/NauEngine/NauEnginePublic/blob/main/engine/core/kernel/include/nau/scripts/script_manager.h#L20>`_ – это основной компонент, отвечающий за
управление скриптами, их загрузку и выполнение. 
Данная статья описывает, как настроить **ScriptManager**, как выполнять скрипты, написанные на **Lua** и как 
использовать **Typescript** для разработки более сложных и поддерживаемых скриптов. 
В бета-версии Nau Engine функциональность **ScriptManager** может быть ограничена.

Настройка путей
----------------

Прежде всего, необходимо настроить пути поиска скриптов. Это можно сделать двумя способами:

1. Напрямую через код: Используйте метод `ScriptManager::addScriptSearchPath <https://github.com/NauEngine/NauEnginePublic/blob/main/engine/core/kernel/include/nau/scripts/script_manager.h#L36>`_ , чтобы добавить путь к папке, где хранятся ваши скрипты.
2. Через файл конфигурации: Более удобный способ – указать пути поиска в файле конфигурации. 
   Например, в JSON-файле конфигурации добавьте секцию ``scripts`` с массивом ``searchPaths``, содержащим виртуальные пути к папкам со скриптами.
   Эти пути могут быть связаны с реальными папками на вашем диске через секцию ``vfs`` (Virtual File System) в конфигурации.
   
   Пример конфигурации в JSON-формате:
      
   .. code-block:: javascript
      :class: larg

      {
         "app":{
            "vfs":{
               "mounts":[
                  {
                     "mountPoint":"/scriptsRoot", //  Виртуальный путь
                     "path":"${sampleProjectDir}/content/scripts/out.**Lua**" // Реальный путь на диске
                  }

               ]
            }
         },

         "scripts":
         {
            "searchPaths": [
               "/scriptsRoot" // Виртуальный путь к скриптам
            ]
         }
      }

   В этом примере виртуальный путь ``/scriptsRoot`` указывает на реальную папку ``${sampleProjectDir}/content/scripts/out.lua`` на вашем диске. 
   **ScriptManager** будет искать скрипты в папке, связанной с виртуальным путем ``/scriptsRoot``. 
   Использование виртуальных путей позволяет абстрагироваться от физического расположения файлов и упрощает управление проектом.

Выполнение скрипта
-------------------

Для выполнения скриптов в Nau Engine используется компонент **ScriptManager**. Доступны два основных способа запуска скриптов:

* Из буфера памяти: `ScriptManager::executeScriptFromBytes <https://github.com/NauEngine/NauEnginePublic/blob/main/engine/core/kernel/include/nau/scripts/script_manager.h#L26>`_ 
  позволяет выполнить скрипт, загруженный в память. Этот подход полезен, если скрипт генерируется динамически или загружается из внешнего источника.
* Напрямую из файла vfs: `ScriptManager::executeScriptFromFile <https://github.com/NauEngine/NauEnginePublic/blob/main/engine/core/kernel/include/nau/scripts/script_manager.h#L28>`_
  выполняет скрипт непосредственно из файла, расположенного в виртуальной файловой системе (VFS). Этот метод использует пути поиска, указанные в конфигурации 
  **ScriptManager**. Движок найдет первый файл с указанным именем в путях поиска и выполнит его.

Оба метода возвращают объект ``Result``, который содержит информацию об успешности выполнения скрипта. В случае ошибки, ``Result`` будет содержать ее описание 
(например, синтаксическая ошибка или ошибка выполнения). Скрипт потенциально может возвращать значение, однако
в текущей бета-версии обработка возвращаемого значения не реализована. Загрузка и выполнение скрипта трактуются как вызов функции без аргументов.

Пример выполнения скрипта на C++:

.. code-block:: cpp
      :class: larg
      :linenos:

      Result<> startupApplication()
      {
      using namespace nau::scripts;

      ScriptManager& scriptManager = getServiceProvider().get<ScriptManager>();
      
      // Поиск файла осуществляется во всех путях, указанных для поиска (будет использован первый найденный файл).
      NauCheckResult(scriptManager.executeScriptFromFile("MyScript1"));

      // ...
      }

В данном примере ``executeScriptFromFile`` ищет файл ``MyScript1`` (например, ``MyScript1.lua``) во всех указанных путях поиска скриптов
и выполняет его. ``NauCheckResult`` проверяет результат выполнения и обрабатывает возможные ошибки.

Отображение C++ классов в скрипт
---------------------------------

Nau Engine позволяет использовать C++ классы в скриптах. Для этого необходимо предоставить движку метаинформацию о типе,
которая впоследствии доступна через Runtime API. Эта метаинформация позволяет скриптам взаимодействовать с C++ объектами и вызывать их методы.

Декларация/экспорт методов
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Для экспорта методов C++ класса в скрипты используются макросы ``NAU_CLASS_METHODS`` и ``CLASS_METHOD``. Макрос ``NAU_CLASS_METHODS``
перечисляет все методы, которые должны быть доступны из скриптов. Макрос ``CLASS_METHOD`` связывает имя метода в скрипте с соответствующим методом C++ класса.

.. code-block:: cpp
      :class: larg

      class MyNativeBinding : public IRefCounted
         {
            NAU_CLASS_(MyNativeBinding, IRefCounted)
            NAU_CLASS_METHODS(
                  CLASS_METHOD(MyNativeBinding, getKeyboardButtonPressed),
                  CLASS_METHOD(MyNativeBinding, spawnItem))

         public:
            bool getKeyboardButtonPressed(input::Key key) const;

            void spawnItem(float x, float y, float z) const;
         };

В этом примере методы ``getKeyboardButtonPressed`` и ``spawnItem`` класса ``MyNativeBinding`` будут доступны для вызова из скриптов.
Параметры и возвращаемые значения экспортируемых методов должны быть совместимы с системой ``RuntimeValue``, которая используется 
для передачи данных между C++ и скриптами.

Декларация/экспорта свойств (properties)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Экспорт свойств (properties) C++ классов в скрипты в текущей бета-версии Nau Engine не поддерживается.

Регистрация класса и создание экземпляра
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Для того чтобы C++ класс стал доступен в скриптах, его необходимо зарегистрировать в **ScriptManager**. Это делается с помощью метода  
`ScriptManager::registerClass <https://github.com/NauEngine/NauEnginePublic/blob/main/engine/core/kernel/include/nau/scripts/script_manager.h#L30>`_ 
или  `ScriptManager::registerNativeClass<Class> <https://github.com/NauEngine/NauEnginePublic/blob/main/engine/core/kernel/include/nau/scripts/script_manager.h#L41>`_ .

.. code-block:: cpp
      :class: larg

      void startupApplication()
      {
         using namespace nau::scripts;

         ScriptManager& scriptManager = getServiceProvider().get<ScriptManager>();
         scriptManager.registerNativeClass<MyNativeBinding>();
      }

После регистрации класса вы можете создавать экземпляры объекта-обертки над C++ типом в ваших скриптах. 
Способ создания экземпляра зависит от используемого языка скриптов.

|

Пример на **Lua**:

.. code-block:: lua
      :class: larg

      binding = MyNativeBinding:New()
      function globalFunction(dt)
         if binding:getKeyboardButtonPressed("A") then
            binding:spawnItem(10, 20, 30)
            print("Key pressed")
         end
         return ("no press (" .. tostring(dt)) .. ")"
      end


Пример на **Typescript**:

.. code-block:: javascript
      :class: larg

      /**
      * Native (C++) Api
      */
      declare class MyNativeBinding {
      public static New(): MyNativeBinding;

      public getKeyboardButtonPressed(key: string): boolean;
      public spawnItem(x: number, y: number, z: number): void;
      }

      const binding = MyNativeBinding.New();

      function globalFunction(dt: number): String {

      if (binding.getKeyboardButtonPressed("A")) {
         binding.spawnItem(10, 20, 30);
         print("Key pressed");

      }

      return `no press (${dt})`
      }

В обоих примерах создается экземпляр класса ``MyNativeBinding`` и вызываются его методы.

Доступ к скриптам из C++
------------------------

Nau Engine позволяет вызывать функции, определенные в скриптах, непосредственно из C++ кода. Это обеспечивает гибкость и 
позволяет использовать скрипты для реализации игровой логики, взаимодействуя с ними из C++.

Вызов глобальной функции
~~~~~~~~~~~~~~~~~~~~~~~~

Для вызова глобальной функции, определенной в скрипте, используется метод `ScriptManager::invokeGlobal <https://github.com/NauEngine/NauEnginePublic/blob/main/engine/core/kernel/include/nau/scripts/script_manager.h#L32>`_
или типизированная обёртка над `invokeGlobal: GlobalFunction\<R (P...)\> <https://github.com/NauEngine/NauEnginePublic/blob/main/engine/core/kernel/include/nau/scripts/scripts.h#L22C12-L22C27>`_,
где R — тип возвращаемого значения, а P... — типы параметров функции. 

.. code-block:: cpp
      :class: larg

      scripts::GlobalFunction<std::string(float)> globalFunction{"globalFunction"};
      // ...
      Result<std::string> invokeRes = globalFunction(0.1f);
      // ...

В этом примере объявляется глобальная функция ``globalFunction``, которая принимает один параметр типа ``float`` и возвращает значение типа ``std::string``. 
Затем функция вызывается с параметром ``0.1f``, и результат сохраняется в переменной ``invokeRes``. Объект ``Result`` содержит возвращаемое значение функции и
информацию об успешности выполнения.

Создание экземпляров классов
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Функциональность создания экземпляров классов скриптов из C++ кода находится в разработке и будет доступна в будущих версиях Nau Engine. 
Следите за обновлениями!*

Использование **Typescript** в Nau Engine
------------------------------------------

В текущей бета-версии Nau Engine для поддержки скриптов разработан модуль **LuaScripts**. 
`Lua <https://www.lua.org/>`_ — это компактный, стабильный и широко распространенный язык, подходящий для встраивания в игровые движки. Он работает на различных платформах и 
имеет JIT-реализации для повышения производительности. Однако, как динамический язык без строгой типизации, **Lua** имеет некоторые недостатки, 
особенно при разработке крупных проектов, например в этом языке "из коробки" нет стандартной поддержки модульности, а отсутствие системы типов влечёт за собой:

* сложность разработки больших проектов;
* сложность поддержки на уровне IDE:  организации даже простейшего intellisense подразумевает нетривиальный анализ всего проекта;
* невозможность декларации внешних типов, т.е. биндинги привносят runtime объекты, но нет возможности (в рамках языка) ввести декларацию типов этих объектов.

Поэтому использование **Lua** позиционируется только в качестве "Backend" - целевой системы исполнения. Тем временем в качестве "Frontend" 
рекомендуется использовать `Typescript <https://www.typescriptlang.org/>`_ , который должен быть использован в качестве основного языка и впоследствии трансформирован в ****Lua**** через инструмент `TypescriptToLua <https://typescripttolua.github.io/>`_.

Настройка проекта **Typescript**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Для работы с **Typescript** в Nau Engine необходимо следующее:

* Установленный `Node.js <https://nodejs.org/en/download/package-manager>`_: **Typescript** и **TypescripToLua** основаны на Node.js.
* Проект оформляется как node package: следуйте инструкциям по настройке проекта в документации  `TypescriptToLua Getting started <https://typescripttolua.github.io/docs/getting-started/>`_
* Файлы ``package.json`` и ``tsconfig.json``: эти файлы содержат настройки проекта и компилятора **Typescript**.

package.json:

.. code-block:: javascript
      :class: larg

      {
      "name": "nau_scripts_sample",
      "version": "1.0.0",

      "scripts": {
         "build": "tstl",
         "dev": "tstl --watch"
      },

      "devDependencies": {
         "Typescript**": "^5.6.2",
         "Typescript-to-Lua": "^1.27.1"
      }
      }

tsconfig.json:

.. code-block:: javascript
      :class: larg

      
      {
      "$schema": "https://raw.githubusercontent.com/TypescriptToLua/TypescriptToLua/master/tsconfig-schema.json",
      "compilerOptions": {
         "target": "ESNext",
         "lib": ["ESNext"],
         "moduleResolution": "Node",
         "types": [],
         "strict": true,
         "outDir": "out.**Lua**",
         "experimentalDecorators": true
      },
      "tstl": {
         "LuaTarget": "5.4",
         "noImplicitSelf": true
      }
      }

В этой статье мы рассмотрели основные аспекты работы со **ScriptManager** в Nau Engine, включая настройку путей поиска скриптов, выполнение 
скриптов из памяти и из файлов, а также использование **Typescript** для разработки скриптов. Понимание этих принципов позволит вам эффективно 
использовать скрипты для реализации игровой логики и создания интерактивных приложений. Следите за обновлениями документации, чтобы быть в 
курсе последних изменений и новых возможностей.

