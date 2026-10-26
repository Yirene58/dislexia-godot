"""crear tablas de progreso: intentos, dificultad, logros, estado del jugador

Revision ID: a1f3c9d2e7b4
Revises: 56abdb65616d
Create Date: 2026-10-26 18:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1f3c9d2e7b4'
down_revision = '56abdb65616d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'intentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('world_id', sa.String(length=50), nullable=False),
        sa.Column('nivel', sa.Integer(), nullable=False),
        sa.Column('ejercicio', sa.String(length=100), nullable=False),
        sa.Column('respuesta', sa.JSON(), nullable=True),
        sa.Column('correcto', sa.Boolean(), nullable=False),
        sa.Column('tipo_error', sa.String(length=30), nullable=True),
        sa.Column('tiempo_ms', sa.Integer(), nullable=True),
        sa.Column('dificultad', sa.Integer(), nullable=False),
        sa.Column('es_repeticion', sa.Boolean(), nullable=False),
        sa.Column('por_inactividad', sa.Boolean(), nullable=False),
        sa.Column('completo', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_intentos_character_id', 'intentos', ['character_id'])
    op.create_index('ix_intentos_world_id', 'intentos', ['world_id'])

    op.create_table(
        'dificultad_mundo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('world_id', sa.String(length=50), nullable=False),
        sa.Column('dificultad', sa.Integer(), nullable=False),
        sa.Column('racha_aciertos', sa.Integer(), nullable=False),
        sa.Column('racha_fallos', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('character_id', 'world_id', name='uq_dificultad_personaje_mundo'),
    )
    op.create_index('ix_dificultad_mundo_character_id', 'dificultad_mundo', ['character_id'])

    op.create_table(
        'cambios_dificultad',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('world_id', sa.String(length=50), nullable=False),
        sa.Column('anterior', sa.Integer(), nullable=False),
        sa.Column('nueva', sa.Integer(), nullable=False),
        sa.Column('motivo', sa.String(length=60), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cambios_dificultad_character_id', 'cambios_dificultad', ['character_id'])

    op.create_table(
        'logros',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('world_id', sa.String(length=50), nullable=False),
        sa.Column('codigo', sa.String(length=80), nullable=False),
        sa.Column('obtenido_en', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('character_id', 'codigo', name='uq_logro_personaje_codigo'),
    )
    op.create_index('ix_logros_character_id', 'logros', ['character_id'])

    op.create_table(
        'estado_jugador',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('mundo_actual', sa.String(length=50), nullable=False),
        sa.Column('ejercicio_pendiente', sa.JSON(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('character_id'),
    )


def downgrade():
    op.drop_table('estado_jugador')
    op.drop_index('ix_logros_character_id', table_name='logros')
    op.drop_table('logros')
    op.drop_index('ix_cambios_dificultad_character_id', table_name='cambios_dificultad')
    op.drop_table('cambios_dificultad')
    op.drop_index('ix_dificultad_mundo_character_id', table_name='dificultad_mundo')
    op.drop_table('dificultad_mundo')
    op.drop_index('ix_intentos_world_id', table_name='intentos')
    op.drop_index('ix_intentos_character_id', table_name='intentos')
    op.drop_table('intentos')
