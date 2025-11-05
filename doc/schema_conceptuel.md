## Schéma conceptuel

```plantuml
class Repository {
	gitLink : string
}
class Branch {
	name: string
}
class Commit {
	sha : string
    date : date
    author : string
    message : string
}
class "File" {
	path : string
}
class Function {
    signature : string
    linePosition : number
}
class Complexity {
	value : number
}
class IdentifiableEntity {
	entity : string
}
class Duplication {
    text : string
}

Repository "1" -down-> "*" Commit : "saves"
Commit "1..*" -right-> "1..*" Branch : "describes"
Commit "1" -down-> "1..*" "File" : "makes version of"
"File" "1" -right-> "*" Function : "contains"
"File" "*" -down-> "*" IdentifiableEntity : contains
Complexity "1" -up-> "1" Function : "mesures"
Duplication "*" -right-> "*" File

```
