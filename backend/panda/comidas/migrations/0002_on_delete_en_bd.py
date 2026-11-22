# panda/comidas/migrations/0002_on_delete_en_bd.py
from django.db import migrations

# (tabla, columna, tabla_referenciada, acción, nombre_del_constraint)
FKS = [
    ("perfiles", "usuario_id", "usuarios", "CASCADE", "fk_perfiles_usuario"),
    ("consentimientos", "usuario_id", "usuarios", "CASCADE", "fk_consentimientos_usuario"),
    ("preferencias_actividad", "usuario_id", "usuarios", "CASCADE", "fk_preferencias_usuario"),
    ("preferencias_actividad", "actividad_id", "actividades", "RESTRICT", "fk_preferencias_actividad"),
    ("comidas", "usuario_id", "usuarios", "CASCADE", "fk_comidas_usuario"),
    ("comida_items", "comida_id", "comidas", "CASCADE", "fk_comida_items_comida"),
    ("comida_items", "alimento_id", "alimentos", "SET NULL", "fk_comida_items_alimento"),
    ("correcciones", "comida_id", "comidas", "CASCADE", "fk_correcciones_comida"),
    ("recomendaciones", "comida_id", "comidas", "CASCADE", "fk_recomendaciones_comida"),
    ("recomendacion_items", "recomendacion_id", "recomendaciones", "CASCADE", "fk_recomendacion_items_recomendacion"),
    ("recomendacion_items", "actividad_id", "actividades", "RESTRICT", "fk_recomendacion_items_actividad"),
]


def _redefinir(tabla, columna, referencia, accion, nombre):
    return f"""
    DO $$
    DECLARE r record;
    BEGIN
      FOR r IN
        SELECT con.conname FROM pg_constraint con
        JOIN pg_attribute att ON att.attrelid = con.conrelid AND att.attnum = ANY (con.conkey)
        WHERE con.contype = 'f' AND con.conrelid = '{tabla}'::regclass AND att.attname = '{columna}'
      LOOP
        EXECUTE format('ALTER TABLE {tabla} DROP CONSTRAINT %I', r.conname);
      END LOOP;
    END $$;
    ALTER TABLE {tabla} ADD CONSTRAINT {nombre} FOREIGN KEY ({columna})
      REFERENCES {referencia}(id) ON DELETE {accion} DEFERRABLE INITIALLY DEFERRED;
    """


def _revertir(tabla, columna, referencia, _accion, nombre):
    return f"""
    ALTER TABLE {tabla} DROP CONSTRAINT IF EXISTS {nombre};
    ALTER TABLE {tabla} ADD CONSTRAINT {nombre} FOREIGN KEY ({columna})
      REFERENCES {referencia}(id) DEFERRABLE INITIALLY DEFERRED;
    """


class Migration(migrations.Migration):
    dependencies = [
        ("comidas", "0001_crear_comidas"),
        ("recomendacion", "0001_crear_recomendaciones"),
        ("identidad", "0002_preferencias_actividad"),
    ]
    operations = [migrations.RunSQL(sql=_redefinir(*fk), reverse_sql=_revertir(*fk)) for fk in FKS]