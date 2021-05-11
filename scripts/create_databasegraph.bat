cd /D "E:\beach_handball"
call env\Scripts\activate.bat
python manage.py graph_models -a > database_graph.dot

"C:\Program Files (x86)\Graphviz2.38\bin\dot.exe" -Tpng database_graph.dot -o database.png