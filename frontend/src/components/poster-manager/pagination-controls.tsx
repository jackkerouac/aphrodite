"use client"

import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from "lucide-react"

interface PaginationControlsProps {
  currentPage: number
  totalItems: number
  itemsPerPage: number
  onPageChange: (page: number) => void
  onItemsPerPageChange: (itemsPerPage: number) => void
  loading?: boolean
}

export function PaginationControls({
  currentPage,
  totalItems,
  itemsPerPage,
  onPageChange,
  onItemsPerPageChange,
  loading = false
}: PaginationControlsProps) {
  const totalPages = Math.ceil(totalItems / itemsPerPage)
  const startItem = (currentPage - 1) * itemsPerPage + 1
  const endItem = Math.min(currentPage * itemsPerPage, totalItems)

  if (totalItems === 0) {
    return null
  }

  return (
    <div className="flex items-center justify-between px-2 py-4">
      {/* Items info and per-page selector */}
      <div className="flex items-center space-x-4">
        <div className="text-sm text-muted-foreground">
          Showing {startItem} to {endItem} of {totalItems} items
        </div>
        
        <div className="flex items-center space-x-2">
          <span className="text-sm text-muted-foreground">Show:</span>
          <Select
            value={itemsPerPage.toString()}
            onValueChange={(value) => onItemsPerPageChange(parseInt(value))}
            disabled={loading}
          >
            <SelectTrigger className="w-20">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="25">25</SelectItem>
              <SelectItem value="50">50</SelectItem>
              <SelectItem value="100">100</SelectItem>
              <SelectItem value="200">200</SelectItem>
            </SelectContent>
          </Select>
          <span className="text-sm text-muted-foreground">per page</span>
        </div>
      </div>

      {/* Pagination controls */}
      <div className="flex items-center space-x-2">
        <div className="text-sm text-muted-foreground mr-4">
          Page {currentPage} of {totalPages}
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(1)}
          disabled={currentPage === 1 || loading}
        >
          <ChevronsLeft className="h-4 w-4" />
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1 || loading}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>

        {/* Page numbers */}
        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
          let pageNumber
          if (totalPages <= 5) {
            pageNumber = i + 1
          } else if (currentPage <= 3) {
            pageNumber = i + 1
          } else if (currentPage >= totalPages - 2) {
            pageNumber = totalPages - 4 + i
          } else {
            pageNumber = currentPage - 2 + i
          }

          return (
            <Button
              key={pageNumber}
              variant={pageNumber === currentPage ? "default" : "outline"}
              size="sm"
              onClick={() => onPageChange(pageNumber)}
              disabled={loading}
              className="w-8"
            >
              {pageNumber}
            </Button>
          )
        })}

        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages || loading}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(totalPages)}
          disabled={currentPage === totalPages || loading}
        >
          <ChevronsRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
