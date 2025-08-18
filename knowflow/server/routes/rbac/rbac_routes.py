#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RBAC权限管理路由
提供角色、权限管理的API接口
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from flask import Blueprint, request, jsonify, g
from typing import Optional
import logging
from datetime import datetime, timedelta
from services.rbac.permission_service import permission_service
# 移除中间件装饰器的导入
# from services.rbac.permission_decorator import (
#     require_login, admin_required, super_admin_required,
#     require_permission, require_role
# )
from models.rbac_models import ResourceType, PermissionType, RoleType

logger = logging.getLogger(__name__)

# 创建蓝图
rbac_bp = Blueprint('rbac', __name__, url_prefix='/api/v1/rbac')

@rbac_bp.route('/permissions/check', methods=['POST'])
def check_permission():
    """
    检查用户权限
    
    Request Body:
    {
        "resource_type": "knowledgebase",
        "resource_id": "kb_123",
        "permission_type": "read",
        "user_id": "user_123"  // 可选，默认为当前用户
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': '请求数据不能为空',
                'code': 400
            }), 400
        
        # 验证必需参数
        required_fields = ['resource_type', 'resource_id', 'permission_type', 'user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'缺少必需参数: {field}',
                    'code': 400
                }), 400
        
        # 解析参数
        try:
            resource_type = ResourceType(data['resource_type'])
            permission_type = PermissionType(data['permission_type'])
        except ValueError as e:
            return jsonify({
                'error': f'无效的参数值: {str(e)}',
                'code': 400
            }), 400
        
        resource_id = data['resource_id']
        user_id = data['user_id']
        tenant_id = data.get('tenant_id', 'default')
        
        # 执行权限检查
        permission_check = permission_service.check_permission(
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            permission_type=permission_type,
            tenant_id=tenant_id
        )
        
        return jsonify({
            'has_permission': permission_check.has_permission,
            'user_id': permission_check.user_id,
            'resource_type': permission_check.resource_type.value,
            'resource_id': permission_check.resource_id,
            'permission_type': permission_check.permission_type.value,
            'granted_roles': permission_check.granted_roles,
            'reason': permission_check.reason
        })
        
    except Exception as e:
        logger.error(f"权限检查失败: {e}")
        return jsonify({
            'error': '权限检查失败',
            'message': str(e),
            'code': 500
        }), 500

@rbac_bp.route('/permissions/check-global', methods=['POST'])
def check_global_permission():
    """
    检查用户全局权限
    
    Request Body:
    {
        "user_id": "user123",
        "permission_type": "write",
        "tenant_id": "tenant123"  // 可选
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': '请求数据不能为空',
                'code': 400
            }), 400
        
        user_id = data.get('user_id')
        permission_type = data.get('permission_type')
        tenant_id = data.get('tenant_id', 'default')
        
        if not user_id or not permission_type:
            return jsonify({
                'error': '缺少必需参数: user_id, permission_type',
                'code': 400
            }), 400
        
        # 解析权限类型
        try:
            perm_type = PermissionType(permission_type)
        except ValueError:
            return jsonify({
                'error': f'无效的权限类型: {permission_type}',
                'code': 400
            }), 400
        
        # 执行全局权限检查
        permission_check = permission_service.check_global_permission(
            user_id=user_id,
            permission_type=perm_type,
            tenant_id=tenant_id
        )
        
        return jsonify({
            'has_permission': permission_check.has_permission,
            'user_id': permission_check.user_id,
            'resource_type': permission_check.resource_type.value,
            'resource_id': permission_check.resource_id,
            'permission_type': permission_check.permission_type.value,
            'granted_roles': permission_check.granted_roles,
            'reason': permission_check.reason
        })
        
    except Exception as e:
        logger.error(f"全局权限检查失败: {e}")
        return jsonify({
            'error': '全局权限检查失败',
            'message': str(e),
            'code': 500
        }), 500

@rbac_bp.route('/users/<user_id>/roles', methods=['GET'])
def get_user_roles(user_id: str):
    """
    获取用户的所有角色
    """
    try:
        tenant_id = request.args.get('tenant_id', 'default')
        roles = permission_service.get_user_roles(user_id, tenant_id)
        
        roles_data = []
        for role in roles:
            roles_data.append({
                'id': role.id,
                'name': role.name,
                'code': role.code,
                'description': role.description,
                'role_type': role.role_type.value,
                'is_system': role.is_system,
                'tenant_id': role.tenant_id,
                'created_at': role.created_at.isoformat() if role.created_at else None,
                'updated_at': role.updated_at.isoformat() if role.updated_at else None
            })
        
        return jsonify({
            'user_id': user_id,
            'roles': roles_data,
            'total': len(roles_data)
        })
        
    except Exception as e:
        logger.error(f"获取用户角色失败: {e}")
        return jsonify({
            'error': '获取用户角色失败',
            'message': str(e),
            'code': 500
        }), 500

@rbac_bp.route('/users/<user_id>/permissions', methods=['GET'])
def get_user_permissions(user_id: str):
    """
    获取用户的所有权限
    """
    try:
        tenant_id = request.args.get('tenant_id', 'default')
        resource_type_param = request.args.get('resource_type')
        
        resource_type = None
        if resource_type_param:
            try:
                resource_type = ResourceType(resource_type_param)
            except ValueError:
                return jsonify({
                    'error': f'无效的资源类型: {resource_type_param}',
                    'code': 400
                }), 400
        
        permissions = permission_service.get_user_permissions(user_id, resource_type, tenant_id)
        
        permissions_data = []
        for permission in permissions:
            permissions_data.append({
                'id': permission.id,
                'name': permission.name,
                'code': permission.code,
                'description': permission.description,
                'resource_type': permission.resource_type.value,
                'permission_type': permission.permission_type.value,
                'created_at': permission.created_at.isoformat() if permission.created_at else None,
                'updated_at': permission.updated_at.isoformat() if permission.updated_at else None
            })
        
        return jsonify({
            'user_id': user_id,
            'permissions': permissions_data,
            'total': len(permissions_data),
            'resource_type_filter': resource_type_param
        })
        
    except Exception as e:
        logger.error(f"获取用户权限失败: {e}")
        return jsonify({
            'error': '获取用户权限失败',
            'message': str(e),
            'code': 500
        }), 500

@rbac_bp.route('/users/<user_id>/roles', methods=['POST'])
def grant_role_to_user(user_id: str):
    """
    为用户授予角色
    
    Request Body:
    {
        "role_code": "editor",
        "tenant_id": "tenant_123",  // 可选
        "resource_type": "knowledgebase",  // 可选，用于资源级权限
        "resource_id": "kb_123",  // 可选，用于资源级权限
        "expires_at": "2024-12-31T23:59:59"  // 可选，过期时间
    }
    """
    try:
        data = request.get_json()
        if not data or 'role_code' not in data:
            return jsonify({
                'error': '缺少必需参数: role_code',
                'code': 400
            }), 400
        
        role_code = data['role_code']
        tenant_id = data.get('tenant_id', 'default')
        resource_type = None
        resource_id = data.get('resource_id')
        expires_at = None
        
        # 验证角色代码是否有效
        valid_roles = ['super_admin', 'admin', 'editor', 'viewer', 'user']
        if role_code not in valid_roles:
            return jsonify({
                'error': f'无效的角色代码: {role_code}',
                'code': 400
            }), 400
        
        # 解析资源类型
        if 'resource_type' in data:
            try:
                resource_type = ResourceType(data['resource_type'])
            except ValueError:
                return jsonify({
                    'error': f'无效的资源类型: {data["resource_type"]}',
                    'code': 400
                }), 400
        
        # 解析过期时间
        if 'expires_at' in data:
            try:
                expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'error': '无效的过期时间格式',
                    'code': 400
                }), 400
        
        # 授予角色
        success = permission_service.grant_role_to_user(
            user_id=user_id,
            role_code=role_code,
            granted_by='system',
            tenant_id=tenant_id,
            resource_type=resource_type,
            resource_id=resource_id,
            expires_at=expires_at
        )
        
        if success:
            return jsonify({
                'message': f'成功为用户 {user_id} 授予角色 {role_code}',
                'user_id': user_id,
                'role_code': role_code,
                'granted_by': 'system',
                'tenant_id': tenant_id,
                'resource_type': resource_type.value if resource_type else None,
                'resource_id': resource_id,
                'expires_at': expires_at.isoformat() if expires_at else None
            })
        else:
            return jsonify({
                'error': '授予角色失败',
                'code': 500
            }), 500
        
    except Exception as e:
        logger.error(f"授予角色失败: {e}")
        return jsonify({
            'error': '授予角色失败',
            'message': str(e),
            'code': 500
        }), 500

@rbac_bp.route('/users/<user_id>/roles/<role_code>', methods=['DELETE'])
def revoke_role_from_user(user_id: str, role_code: str):
    """
    撤销用户角色
    """
    try:
        tenant_id = request.args.get('tenant_id', 'default')
        resource_id = request.args.get('resource_id')
        
        success = permission_service.revoke_role_from_user(
            user_id=user_id,
            role_code=role_code,
            tenant_id=tenant_id,
            resource_id=resource_id
        )
        
        if success:
            return jsonify({
                'message': f'成功撤销用户 {user_id} 的角色 {role_code}',
                'user_id': user_id,
                'role_code': role_code,
                'tenant_id': tenant_id,
                'resource_id': resource_id
            })
        else:
            return jsonify({
                'error': '撤销角色失败',
                'code': 500
            }), 500
        
    except Exception as e:
        logger.error(f"撤销角色失败: {e}")
        return jsonify({
            'error': '撤销角色失败',
            'message': str(e),
            'code': 500
        }), 500

@rbac_bp.route('/permissions/simple-check', methods=['POST'])
def simple_permission_check():
    """
    简化的权限检查接口
    
    Request Body:
    {
        "permission_code": "kb_read",
        "resource_id": "kb_123",  // 可选
        "user_id": "user_123"  // 必需
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': '请求数据不能为空',
                'code': 400
            }), 400
        
        required_fields = ['permission_code', 'user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'缺少必需参数: {field}',
                    'code': 400
                }), 400
        
        permission_code = data['permission_code']
        resource_id = data.get('resource_id')
        user_id = data['user_id']
        tenant_id = data.get('tenant_id', 'default')
        
        has_permission = permission_service.has_permission(
            user_id=user_id,
            permission_code=permission_code,
            resource_id=resource_id,
            tenant_id=tenant_id
        )
        
        return jsonify({
            'has_permission': has_permission,
            'user_id': user_id,
            'permission_code': permission_code,
            'resource_id': resource_id,
            'tenant_id': tenant_id
        })
        
    except Exception as e:
        logger.error(f"简化权限检查失败: {e}")
        return jsonify({
            'error': '权限检查失败',
            'message': str(e),
            'code': 500
        }), 500

@rbac_bp.route('/roles', methods=['GET'])
def get_all_roles():
    """
    获取所有角色列表
    """
    try:
        roles = permission_service.get_all_roles()
        
        roles_data = []
        for role in roles:
            roles_data.append({
                'id': role.id,
                'name': role.name,
                'code': role.code,
                'description': role.description,
                'role_type': role.role_type.value,
                'is_system': role.is_system,
                'tenant_id': role.tenant_id,
                'created_at': role.created_at.isoformat() if role.created_at else None,
                'updated_at': role.updated_at.isoformat() if role.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'data': roles_data,
            'total': len(roles_data)
        })
        
    except Exception as e:
        logger.error(f"获取角色列表失败: {e}")
        return jsonify({
            'success': False,
            'error': '获取角色列表失败',
            'message': str(e),
            'code': 500
        }), 500

@rbac_bp.route('/my/roles', methods=['GET'])
def get_my_roles():
    """
    获取指定用户的角色
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'error': '缺少必需参数: user_id',
                'code': 400
            }), 400
        
        tenant_id = request.args.get('tenant_id', 'default')
        roles = permission_service.get_user_roles(user_id, tenant_id)
        
        roles_data = []
        for role in roles:
            roles_data.append({
                'id': role.id,
                'name': role.name,
                'code': role.code,
                'description': role.description,
                'role_type': role.role_type.value,
                'is_system': role.is_system,
                'tenant_id': role.tenant_id
            })
        
        return jsonify({
            'user_id': user_id,
            'roles': roles_data,
            'total': len(roles_data)
        })
        
    except Exception as e:
        logger.error(f"获取当前用户角色失败: {e}")
        return jsonify({
            'error': '获取角色失败',
            'message': str(e),
            'code': 500
        }), 500

@rbac_bp.route('/my/permissions', methods=['GET'])
def get_my_permissions():
    """
    获取指定用户的权限
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'error': '缺少必需参数: user_id',
                'code': 400
            }), 400
        
        tenant_id = request.args.get('tenant_id', 'default')
        resource_type_param = request.args.get('resource_type')
        
        resource_type = None
        if resource_type_param:
            try:
                resource_type = ResourceType(resource_type_param)
            except ValueError:
                return jsonify({
                    'error': f'无效的资源类型: {resource_type_param}',
                    'code': 400
                }), 400
        
        permissions = permission_service.get_user_permissions(user_id, resource_type, tenant_id)
        
        permissions_data = []
        for permission in permissions:
            permissions_data.append({
                'id': permission.id,
                'name': permission.name,
                'code': permission.code,
                'description': permission.description,
                'resource_type': permission.resource_type.value,
                'permission_type': permission.permission_type.value
            })
        
        return jsonify({
            'user_id': user_id,
            'permissions': permissions_data,
            'total': len(permissions_data),
            'resource_type_filter': resource_type_param
        })
        
    except Exception as e:
        logger.error(f"获取当前用户权限失败: {e}")
        return jsonify({
            'error': '获取权限失败',
            'message': str(e),
            'code': 500
        }), 500

@rbac_bp.route('/permissions', methods=['GET'])
def get_all_permissions():
    """获取所有权限列表"""
    try:
        permissions = permission_service.get_all_permissions()
        return jsonify(permissions)
    except Exception as e:
        logger.error(f"获取权限列表失败: {str(e)}")
        return jsonify({
            'error': f'获取权限列表失败: {str(e)}',
            'code': 500
        }), 500

@rbac_bp.route('/roles/<role_code>/permissions', methods=['GET'])
def get_role_permissions(role_code: str):
    """获取角色权限映射"""
    try:
        permissions = permission_service.get_role_permissions(role_code)
        return jsonify(permissions)
    except Exception as e:
        logger.error(f"获取角色权限映射失败: {str(e)}")
        return jsonify({
            'error': f'获取角色权限映射失败: {str(e)}',
            'code': 500
        }), 500

@rbac_bp.route('/health', methods=['GET'])
def health_check():
    """
    RBAC系统健康检查
    """
    return jsonify({
        'status': 'healthy',
        'service': 'RBAC权限管理系统',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

# 错误处理
@rbac_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': '请求参数错误',
        'message': str(error),
        'code': 400
    }), 400

@rbac_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'error': '未授权访问',
        'message': '请先登录',
        'code': 401
    }), 401

@rbac_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'error': '权限不足',
        'message': '您没有执行此操作的权限',
        'code': 403
    }), 403

@rbac_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': '服务器内部错误',
        'message': '系统异常，请稍后重试',
        'code': 500
    }), 500