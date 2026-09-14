{% macro surrogate_key(columns) -%}
md5(concat_ws('||', {% for column in columns %}coalesce(cast({{ column }} as text), '_null_'){% if not loop.last %}, {% endif %}{% endfor %}))
{%- endmacro %}
