with v as (
    with f as (
        select file.id as file_id, file.name as file_name from file 
        join commit on commit.id = file.commit_id
        where file.commit_id like '@'
    )
    select 
        f.file_id, 
        f.file_name, 
        duplicated_lines, 
        todo_count, 
        avg_cmplx, 
        b_fn_count, 
        low_risk_fn_count, 
        mod_risk_fn_count, 
        high_risk_fn_count, 
        very_high_risk_fn_count
    from f
    left join (
        select 
            f.file_id as file_id, 
            coalesce(sum(file_duplication.end_line - file_duplication.start_line), 0) as duplicated_lines, 
            count(file_identifiable_entity.id) as todo_count
        from f 
        left join file_identifiable_entity on file_identifiable_entity.file_id = f.file_id
        left join file_duplication on file_duplication.file_id = f.file_id
        group by f.file_id
    ) dup_todo on dup_todo.file_id = f.file_id
    left join (
        select 
            f.file_id as file_id,  
            avg(case when complexity.value is null then 0 else complexity.value end) as avg_cmplx, 
            sum(case when complexity.value < 10 then 1 else 0 end) as low_risk_fn_count,
            sum(case when complexity.value >= 11 and complexity.value < 21 then 1 else 0 end) as mod_risk_fn_count,
            sum(case when complexity.value >= 21 and complexity.value < 50 then 1 else 0 end) as high_risk_fn_count,
            sum(case when complexity.value >= 51 then 1 else 0 end) as very_high_risk_fn_count,
            sum(case when size.value is null or size.value < 150 then 0 else 1 end) as b_fn_count 
        from f 
        left join function on function.file_id = f.file_id
        left join complexity on complexity.function_id = function.id
        left join size on size.function_id = function.id 
        group by f.file_id
    ) func_stats on func_stats.file_id = f.file_id
)
select 
    *,
    (
        (duplicated_lines / (case when max_dupl_lines = 0 then 1 else max_dupl_lines end) * 0.27) + 
        (avg_cmplx / (case when max_avg_cmplx = 0 then 1 else max_avg_cmplx end) * 0.37) + 
        (todo_count / (case when max_todo_count = 0 then 1 else max_todo_count end) * 0.26) + 
        (b_fn_count / (case when max_b_fn_count = 0 then 1 else max_b_fn_count end) * 0.10)
    ) as score
from v, 
(select max(v.duplicated_lines) as max_dupl_lines from v),
(select max(v.todo_count) as max_todo_count from v),
(select max(v.avg_cmplx) as max_avg_cmplx from v),
(select max(v.b_fn_count) as max_b_fn_count from v)
order by score desc

-- https://en.wikipedia.org/wiki/Cyclomatic_complexity