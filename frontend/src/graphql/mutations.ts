/**
 * GraphQL Mutations
 *
 * All mutations for creating, updating, and deleting data.
 */

import { gql } from '@apollo/client';

// ============================================================================
// PRODUCT MUTATIONS
// ============================================================================

export const CREATE_PRODUCT = gql`
  mutation CreateProduct($input: ProductInput!) {
    createProduct(input: $input) {
      id
      name
      sku
      price
      costPrice
      stockQuantity
      categoryId
      isActive
      createdAt
    }
  }
`;

export const UPDATE_PRODUCT = gql`
  mutation UpdateProduct($id: Int!, $input: ProductInput!) {
    updateProduct(id: $id, input: $input) {
      id
      name
      sku
      price
      costPrice
      stockQuantity
      categoryId
      isActive
      updatedAt
    }
  }
`;

export const DELETE_PRODUCT = gql`
  mutation DeleteProduct($id: Int!) {
    deleteProduct(id: $id) {
      success
      message
    }
  }
`;

export const UPDATE_PRODUCT_STOCK = gql`
  mutation UpdateProductStock($id: Int!, $quantity: Int!) {
    updateProductStock(id: $id, quantity: $quantity) {
      id
      name
      stockQuantity
      updatedAt
    }
  }
`;

// ============================================================================
// CUSTOMER MUTATIONS
// ============================================================================

export const CREATE_CUSTOMER = gql`
  mutation CreateCustomer($input: CustomerInput!) {
    createCustomer(input: $input) {
      id
      name
      email
      phone
      city
      state
      country
      createdAt
    }
  }
`;

export const UPDATE_CUSTOMER = gql`
  mutation UpdateCustomer($id: Int!, $input: CustomerInput!) {
    updateCustomer(id: $id, input: $input) {
      id
      name
      email
      phone
      city
      state
      country
      updatedAt
    }
  }
`;

export const DELETE_CUSTOMER = gql`
  mutation DeleteCustomer($id: Int!) {
    deleteCustomer(id: $id) {
      success
      message
    }
  }
`;

export const ASSIGN_CUSTOMER_SEGMENT = gql`
  mutation AssignCustomerSegment($customerId: Int!) {
    assignCustomerSegment(customerId: $customerId) {
      id
      name
      segment
      lifetimeValue
      updatedAt
    }
  }
`;

// ============================================================================
// ORDER MUTATIONS
// ============================================================================

export const CREATE_ORDER = gql`
  mutation CreateOrder($input: OrderInput!) {
    createOrder(input: $input) {
      id
      orderNumber
      customerId
      salesRepId
      orderDate
      totalAmount
      status
      createdAt
    }
  }
`;

export const UPDATE_ORDER = gql`
  mutation UpdateOrder($id: Int!, $input: OrderInput!) {
    updateOrder(id: $id, input: $input) {
      id
      orderNumber
      totalAmount
      status
      updatedAt
    }
  }
`;

export const UPDATE_ORDER_STATUS = gql`
  mutation UpdateOrderStatus($id: Int!, $status: String!) {
    updateOrderStatus(id: $id, status: $status) {
      id
      orderNumber
      status
      updatedAt
    }
  }
`;

export const DELETE_ORDER = gql`
  mutation DeleteOrder($id: Int!) {
    deleteOrder(id: $id) {
      success
      message
    }
  }
`;

export const ADD_ORDER_ITEM = gql`
  mutation AddOrderItem($orderId: Int!, $productId: Int!, $quantity: Int!, $unitPrice: Float!) {
    addOrderItem(orderId: $orderId, productId: $productId, quantity: $quantity, unitPrice: $unitPrice) {
      id
      orderId
      productId
      quantity
      unitPrice
      totalPrice
      createdAt
    }
  }
`;

// ============================================================================
// SALES REP MUTATIONS
// ============================================================================

export const CREATE_SALES_REP = gql`
  mutation CreateSalesRep($input: SalesRepInput!) {
    createSalesRep(input: $input) {
      id
      name
      email
      phone
      territory
      commissionRate
      isActive
      hireDate
    }
  }
`;

export const UPDATE_SALES_REP = gql`
  mutation UpdateSalesRep($id: Int!, $input: SalesRepInput!) {
    updateSalesRep(id: $id, input: $input) {
      id
      name
      email
      phone
      territory
      commissionRate
      isActive
      updatedAt
    }
  }
`;

export const DELETE_SALES_REP = gql`
  mutation DeleteSalesRep($id: Int!) {
    deleteSalesRep(id: $id) {
      success
      message
    }
  }
`;

// ============================================================================
// CATEGORY MUTATIONS
// ============================================================================

export const CREATE_CATEGORY = gql`
  mutation CreateCategory($input: CategoryInput!) {
    createCategory(input: $input) {
      id
      name
      description
      createdAt
    }
  }
`;

export const UPDATE_CATEGORY = gql`
  mutation UpdateCategory($id: Int!, $input: CategoryInput!) {
    updateCategory(id: $id, input: $input) {
      id
      name
      description
      updatedAt
    }
  }
`;

export const DELETE_CATEGORY = gql`
  mutation DeleteCategory($id: Int!) {
    deleteCategory(id: $id) {
      success
      message
    }
  }
`;

// ============================================================================
// CACHE MUTATIONS
// ============================================================================

export const INVALIDATE_CACHE = gql`
  mutation InvalidateCache($pattern: String!) {
    invalidateCache(pattern: $pattern) {
      success
      message
      keysCleared
    }
  }
`;

export const CLEAR_ALL_CACHE = gql`
  mutation ClearAllCache {
    clearAllCache {
      success
      message
    }
  }
`;
