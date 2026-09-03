import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createProduct, deleteProduct, listProducts, ProductInput, updateProduct } from "./api";

const productKey = (businessId: string) => ["products", businessId] as const;

export function useProducts(businessId?: string) {
  return useQuery({
    queryKey: productKey(businessId ?? ""),
    queryFn: () => listProducts(businessId!),
    enabled: Boolean(businessId),
  });
}

export function useCreateProduct(businessId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: ProductInput) => createProduct(businessId, input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: productKey(businessId) }),
  });
}

export function useUpdateProduct(businessId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ productId, input }: { productId: string; input: ProductInput }) =>
      updateProduct(businessId, productId, input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: productKey(businessId) }),
  });
}

export function useDeleteProduct(businessId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (productId: string) => deleteProduct(businessId, productId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: productKey(businessId) }),
  });
}
