# Почему, зачем и что дальше

## Почему

Идея немного "стандартизировать" конфигурацию и отделить её от настроек родилась еще в конце 2021 года.

В моём понимании настройки приложения и конфигурация - это совсем разные вещи:

- В настройках указывается какие именно параметры нужны вашему приложению для нормальной работы.
- А в файлах конфигурации указываются значения этих параметров.

Часто эти два разных понятия путают или объединяют в одно - "Настройки приложения".

На конец 2023 года - начало 2024 года я так и не нашел библиотеку, которая удовлетворяла всем моим потребностям при написании нового приложения. Каждый раз для нового приложения приходилось выдумывать что-то своё.
Думаю как и большинство из вас, я использовал настройки из библиотеки [Pydantic](https://github.com/pydantic/pydantic). Раньше они были встроены, если мне память не изменяет, но с появлением `pydantic 2.x` их вынесли в отдельную библиотеку [pydantic-settings](https://github.com/pydantic/pydantic-settings).
Всё бы ничего, но только мне постоянно `катастрофически` не хватало функционала. Приходилось постоянно дописывать свои "костыли".

Посмотрев на эту ситуацию я принял решение написать свою библиотеку, которая будет полезна не только мне, но и всем разработчикам, которые, как и я, постоянно создают новые приложения используя современные технологии и которые не хотят каждый раз тратить время в самом начале разработки на реализацию того, что должно по умолчанию работать "из коробки".

## Зачем

Так зачем же новая библиотека, если можно было внести вклад в существующую, широко известную, библиотеку `pydantic-settings`?

Используя `pydantic-settings` я каждый раз удивлялся результату.
Что, по моему мнению, в разрешении регистронзависимых имён должно было быть по Определению - не всегда работало.
Я лез гуглить и всегда натыкался на уже созданное issue.

В одном из комментариев к issues я увидел сообщение, что данная проблема может быть решена только в версии 2.0 или даже 3.0, не помню точно, из-за того, что нужно переписывать алгоритмы. На сколько я понял в ближайшее время этим никто заниматься не будет.
Но что же делать прямо сейчас, когда ещё версия 2.0 не вышла?

Осознав, что переписывать существующую библиотеку с нуля никто не будет в ближайшее время, и родилось решение написать свою, в которой будут учтено большинство известных нюансов и реализовано всё для комфортной работы.

Когда я начинал писать эту библиотеку (январь 2024) у `pydantic-settings` не было решения для чтения конфигурации из файлов или из CLI.
К моменту завершения написания данной библиотеки уже всё появилось.

Но, на мой взгляд, `arfi-settings` гораздо гибче в настройках и проще для человеческого восприятия. Хотя "проще" становится только тогда, когда вникнешь в принципы обратного наследования :)

## Что дальше

Я искренне хочу чтоб `arfi-settings` переродилась в версию `pydantic-settings.3.0`.
Но если такого не случится, то я буду дальше развивать и поддерживать `arfi-settings` и надеюсь на Вашу помощь!!!

Так же в планах написать дополнение к этой библиотеке для `FastAPI`, чтоб при разработке при переходе по `/settings` можно было посмотреть все текущие настройки.
Это функция будет работать только в `arfi_debug` режиме. Для git нужен будет hook, чтоб отключить коммиты при дебаг режиме. Но это пока в планах.

Приветствуется Любая помощь !!!
