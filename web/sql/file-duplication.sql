select file.id as file_id, file.name as file_name, file_duplication from file 
join commit on commit.id = file.commit_id
join file_duplication on file_duplication.file_id = file.id
where file.id like '@'