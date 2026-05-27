from __future__ import annotations

import traceback
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import bpy

from .collection import (
    get_collections_hide_viewport,
    get_view_layer_collections_exclude,
    get_view_layer_collections_hide_viewport,
    set_collections_hide_viewport,
    set_view_layer_collections_exclude,
    set_view_layer_collections_hide_viewport,
)
from .object import get_objects_hide_states, set_objects_hide_states


@dataclass
class EditorState:
    mode: Optional[str] = None
    objects_hide_states: Optional[Dict[str, Dict[str, bool]]] = None
    collection_hide_viewport_states: Optional[Dict[str, bool]] = None
    vl_collection_hide_viewport_states: Optional[Dict[str, bool]] = None
    vl_collection_exclude_states: Optional[Dict[str, bool]] = None
    selected_objects: List[str] = field(default_factory=list)
    active_object_name: Optional[str] = None
    active_vertex_group_indices: Dict[str, int] = field(default_factory=dict)
    restore_mode_enabled: bool = True
    restore_selection_enabled: bool = True
    restore_visibility_enabled: bool = True
    restore_active_vertex_group_enabled: bool = True

    def restore_state(
        self,
        selected: Optional[List[bpy.types.Object]] = None,
        active: Optional[bpy.types.Object] = None,
    ) -> None:
        if self.restore_mode_enabled and bpy.context.object is not None and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        if self.restore_selection_enabled:
            try:
                bpy.ops.object.select_all(action="DESELECT")
            except RuntimeError:
                pass

        if self.restore_visibility_enabled:
            if self.objects_hide_states is not None:
                set_objects_hide_states(self.objects_hide_states)
            if self.collection_hide_viewport_states is not None:
                set_collections_hide_viewport(self.collection_hide_viewport_states)
            if self.vl_collection_hide_viewport_states is not None:
                set_view_layer_collections_hide_viewport(self.vl_collection_hide_viewport_states)
            if self.vl_collection_exclude_states is not None:
                set_view_layer_collections_exclude(self.vl_collection_exclude_states)

        if self.restore_selection_enabled:
            self._restore_active_object(active)
            self._restore_selected_objects(selected)

        if self.restore_active_vertex_group_enabled:
            self._restore_active_vertex_groups()

        if self.restore_mode_enabled and bpy.context.view_layer.objects.active and self.mode not in {None, "OBJECT"}:
            bpy.ops.object.mode_set(mode=self.mode)

    def try_restore(
        self,
        selected: Optional[List[bpy.types.Object]] = None,
        active: Optional[bpy.types.Object] = None,
    ) -> None:
        try:
            self.restore_state(selected=selected, active=active)
        except Exception as ex:
            print(f"Unable to restore state: {str(ex)}")
            print(traceback.format_exc())

    def _restore_active_object(self, active: Optional[bpy.types.Object]) -> None:
        try:
            if active is not None:
                bpy.context.view_layer.objects.active = active
            elif self.active_object_name:
                bpy.context.view_layer.objects.active = bpy.data.objects.get(self.active_object_name)
        except RuntimeError:
            print("Unable to set active object")

    def _restore_selected_objects(self, selected: Optional[List[bpy.types.Object]]) -> None:
        objects = selected if selected is not None else [
            bpy.data.objects.get(obj_name) for obj_name in self.selected_objects
        ]
        for obj in objects:
            if obj is not None:
                try:
                    obj.select_set(True)
                except RuntimeError:
                    pass

    def _restore_active_vertex_groups(self) -> None:
        for obj_name, active_index in self.active_vertex_group_indices.items():
            obj = bpy.data.objects.get(obj_name)
            if obj is not None and hasattr(obj, "vertex_groups") and len(obj.vertex_groups) > 0:
                obj.vertex_groups.active_index = min(max(0, active_index), len(obj.vertex_groups) - 1)

    @staticmethod
    def capture_current_state(
        *,
        restore_mode: bool = True,
        restore_selection: bool = True,
        restore_visibility: bool = True,
        restore_active_vertex_group: bool = True,
    ) -> "EditorState":
        current_object = bpy.context.object
        current_active_object = bpy.context.view_layer.objects.active

        return EditorState(
            mode=current_object.mode if restore_mode and current_object else None,
            objects_hide_states=get_objects_hide_states() if restore_visibility else None,
            collection_hide_viewport_states=get_collections_hide_viewport() if restore_visibility else None,
            vl_collection_hide_viewport_states=(
                get_view_layer_collections_hide_viewport() if restore_visibility else None
            ),
            vl_collection_exclude_states=get_view_layer_collections_exclude() if restore_visibility else None,
            selected_objects=[obj.name for obj in bpy.context.selected_objects] if restore_selection else [],
            active_object_name=current_active_object.name if restore_selection and current_active_object else None,
            active_vertex_group_indices={
                obj.name: obj.vertex_groups.active_index
                for obj in bpy.data.objects
                if restore_active_vertex_group and obj.type == "MESH" and hasattr(obj, "vertex_groups")
            },
            restore_mode_enabled=restore_mode,
            restore_selection_enabled=restore_selection,
            restore_visibility_enabled=restore_visibility,
            restore_active_vertex_group_enabled=restore_active_vertex_group,
        )
