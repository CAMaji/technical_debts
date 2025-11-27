for file in $(find ./doc/wiki/puml -name '*.puml')
do
    plantuml $file -svg
done