for file in $(find ./doc/wiki/puml -name '*.puml')
do
    java -jar plantuml/plantuml.jar $file -svg
done