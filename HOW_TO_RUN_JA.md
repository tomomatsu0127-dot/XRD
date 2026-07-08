# 起動方法

## このPCで起動する

`outputs/labplot_studio_desktop` フォルダを開いて、次のどちらかをダブルクリックしてください。

- `run_labplot_studio.bat`
- `run_laptop_studio.bat`

このPCでは、Codexに同梱されているPythonを優先して使うように修正済みです。

## 別のノートPCで起動する

現時点の成果物は「完成EXE」ではなく、Pythonで動くデスクトップアプリの土台です。

別PCで使う場合は、まず Python 3.10 以上を入れてから `run_labplot_studio.bat` を実行してください。

将来的には PyInstaller で `LabPlotStudio.exe` に固めれば、Pythonを別途入れずに使える形にできます。

## 起動しない時

黒い画面に `Python was not found.` と出る場合は、そのPCにPythonが入っていません。

黒い画面が一瞬で閉じる場合は、`run_labplot_studio.bat` を右クリックして「編集」を選び、最後に `pause` が入っているか確認してください。今回の版では、Pythonが見つからない時に画面が閉じないようにしてあります。

