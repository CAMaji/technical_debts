## Schéma relationnel (PostgreSQL)

```plantuml

!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&key></color> x
!define column(x) <color:#efefef><&media-record></color> x
!define table(x) object x << (T, white) >>
!define nullable <b><color:#098229>[N]</color></b>
!define unique <b><color:#091782>[U]</color></b>
!define pkey <b><color:#b8861b>[PK]</color></b>
!define fkey <b><color:#000000>[FK]</color></b>
!define space <b>         </b>
hide circle
skinparam classAttributeIconSize 0

table(repository) {
	primary_key(id) : String(36) pkey
    ---
    column(owner) : Text
    column(name) : Text
}

table(branch) {
	primary_key(id) : String(36) pkey
    ---
    foreign_key(repository_id) : String(36) fkey
    ---
    column(name) : Text
}

table(commit) {
    primary_key(id) : String(36) pkey
    ---
    foreign_key(branch_id) : String fkey
	---
    column(sha) : Text
    column(date) : DateTime
    column(author) : Text
    column(message) : Text nullable
}

table(file) {
    primary_key(id) : String(36) pkey
    ---
    foreign_key(commit_id) : String(36) fkey
	---
    column(name) : Text
}

table(function) {
    primary_key(id) : String(36) pkey
    ---
    foreign_key(file_id) : String(36) fkey
    ---
    column(name) : Text
    column(line_position) : Integer
}

table(complexity) {
	primary_key(id) : String(36) pkey
    ---
    foreign_key(function_id) : String(36) fkey
    ---
    column(value) : Integer
}

table(file_identifiable_entity) {
    primary_key(id) : String(36) pkey
    ---
    foreign_key(file_id) : String(36) fkey
    foreign_key(identifiable_entity_id) : String(36) fkey
    --- 
    column(line_position) : Integer
}

table(identifiable_entity) {
	primary_key(id) : String(36) pkey
    ---
    column(name) : Text
}

table(file_duplication) {
    primary_key(id) : String(36) pkey
    ---
    foreign_key(file_id) : String(36) fkey
    foreign_key(duplication_id) : String(36) fkey
}

table(duplication) {
    primary_key(id) : String(36) pkey
    ---
    column(text) : String(10000)
}

branch "1..*" -up-> "1" repository
commit "1..*" -up-> "1" branch
file "1..*" -up-> "1" commit
function "0..*" -left-> "1" file : space
complexity "1" -up-> "1" function
file_duplication "*" -up-> "1" file
file_duplication "*" -down-> "1" duplication
file_identifiable_entity "*" -up-> "1" file
file_identifiable_entity "*" -down-> "1" identifiable_entity

```
---

#### Référence pour la base du style: 
Diakogiannis, A. D. (2024, March 8). Database modeling tutorial using PlantUML. JEE.gr. https://jee.gr/database-modeling-tutorial-using-plantuml/
