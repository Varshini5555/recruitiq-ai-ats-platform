interface Props {
  title: string;
  children: React.ReactNode;
}

export default function SectionCard({
  title,
  children,
}: Props) {
  return (
    <div className="bg-white rounded-3xl shadow-sm border p-6 space-y-5">

      <h2 className="text-2xl font-bold">
        {title}
      </h2>

      {children}

    </div>
  );
}