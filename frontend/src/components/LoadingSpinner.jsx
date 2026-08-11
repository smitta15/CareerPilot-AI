export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-10">
      <div className="h-10 w-10 rounded-full border-4 border-indigo-500 border-t-transparent animate-spin" />
    </div>
  )
}
