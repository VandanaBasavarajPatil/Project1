from rest_framework import permissions


class IsScrumMasterOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow Scrum Masters to edit objects.
    Employees can only read objects they're associated with.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed to Scrum Masters
        return (request.user and 
                request.user.is_authenticated and 
                request.user.role == 'SCRUM_MASTER')


class IsScrumMaster(permissions.BasePermission):
    """
    Permission that only allows Scrum Masters to access.
    """
    
    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                request.user.role == 'SCRUM_MASTER')


class IsProjectMemberOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow project members to edit, others can only read.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions require authentication
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for project members
        if hasattr(obj, 'team_members'):
            return obj.team_members.filter(id=request.user.id).exists()
        
        # For tasks, check if user is a member of the associated project
        if hasattr(obj, 'project') and obj.project:
            return obj.project.team_members.filter(id=request.user.id).exists()
        
        # Default to Scrum Master only
        return request.user.role == 'SCRUM_MASTER'


class IsOwnerOrScrumMaster(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or Scrum Masters to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed to the owner or Scrum Masters
        if hasattr(obj, 'created_by'):
            is_owner = obj.created_by == request.user
        elif hasattr(obj, 'user'):
            is_owner = obj.user == request.user
        else:
            is_owner = False
            
        is_scrum_master = request.user.role == 'SCRUM_MASTER'
        
        return is_owner or is_scrum_master


class IsAssignedOrScrumMaster(permissions.BasePermission):
    """
    Custom permission for tasks - allows assigned user or Scrum Master to edit.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions for assigned user or Scrum Master
        is_assigned = hasattr(obj, 'assigned_to') and obj.assigned_to == request.user
        is_creator = hasattr(obj, 'created_by') and obj.created_by == request.user
        is_scrum_master = request.user.role == 'SCRUM_MASTER'
        
        return is_assigned or is_creator or is_scrum_master


class CanAccessProject(permissions.BasePermission):
    """
    Permission to check if user can access a project.
    Scrum Masters can access all projects.
    Employees can only access projects they're team members of.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'SCRUM_MASTER':
            return True
        
        # Check if user is a team member of the project
        return obj.team_members.filter(id=request.user.id).exists()


class CanAccessTask(permissions.BasePermission):
    """
    Permission to check if user can access a task.
    Scrum Masters can access all tasks.
    Employees can only access tasks assigned to them or in projects they're part of.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'scrum_master':
            return True
        
        # Check if user is assigned to the task
        if obj.assigned_to == request.user:
            return True
        
        # Check if user is in the project team
        if obj.project and obj.project.team_members.filter(id=request.user.id).exists():
            return True
        
        # Check if user created the task
        if obj.created_by == request.user:
            return True
        
        return False