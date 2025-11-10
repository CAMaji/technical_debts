-- Code SQL pour la priorisation des fichiers --

with m as ( -- on 'précalcule' une table avec le nombre de todo et le nombre de lignes dupliquées pour tous les fichiers d'un commit
    select * from (
        select 
            file.id as file_id, 
            file.name as file_name, 
            coalesce(sum(file_duplication.end_line - file_duplication.start_line), 0) as duplicated_lines, 
            count(file_identifiable_entity.id) as todo_count
        from file
        join commit on commit.id = file.commit_id
        left join file_identifiable_entity on file_identifiable_entity.file_id = file.id
        left join file_duplication on file_duplication.file_id = file.id
        where file.commit_id like '0384e614-1d9a-4c97-89f9-6f6b821225ca' -- un ID de commit en exemple
        group by file.id
    ) r
    left join (
        select file_id, avg(value) as avg_complexity from function
        join complexity on complexity.function_id = function.id
        group by file_id
    ) c on c.file_id = r.file_id -- la raison pour laquelle on fait la complexité après les todo et les duplications
)                                -- c'est que la complexité ne dépend pas directement du ficher (mais plutôt de la fonction), 
                                 -- alors que les todo/duplications ont une dépendance directe avec le ficher. Il faut
                                 -- donc faire la jointure en deux étapes.
 
select *, ((duplicated_lines / max_dupl_lines * 0.30) + (avg_complexity / max_avg_complxty * 0.40) + (todo_count / max_todo_count * 0.30)) as score
from 
    m,                                                       -- la table précalculée nous permet ensuite de l'utiliser comme une table régulière;
    (select max(duplicated_lines) as max_dupl_lines from m), 
    (select max(todo_count) as max_todo_count from m),       -- produit cartésien: ajoute une colonne à chaque rangée contenant la valeur maximale 
    (select max(avg_complexity) as max_avg_complxty from m)  -- trouvée dans la table 'm' pour chaque métrique; permet de calculer le score.
order by score desc -- on tri les rangées par le score calculé en ordre décroissant 
